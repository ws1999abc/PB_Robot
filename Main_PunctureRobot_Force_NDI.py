# -*- coding: utf-8 -*-
"""Main control program for a force-guided, NDI-tracked lung puncture robot."""

import csv
import os
import sys
import threading
import time
from datetime import datetime

import keyboard
import numpy as np
import pandas as pd
import serial
import SRI_class
from Falcon_dll import Falcon
from maxon_core import MaxonMotor
from scipy.spatial.transform import Rotation as R
from sksurgerynditracker.nditracker import NDITracker


button_states = [False, False, False, False]
velocity = [0.0, 0.0, 0.0]

# Global lock reserved for synchronized CSV writing.
csv_lock = threading.Lock()

# Timestamp used in output file names.
current_time = datetime.now().strftime("%Y%m%d-%H-%M-%S")

# Store output beside this script so execution is independent of the working directory.
script_directory = os.path.dirname(os.path.abspath(__file__))
force_data_directory = os.path.join(script_directory, "Force_NDI_data")
ndi_data_directory = os.path.join(script_directory, "result")
os.makedirs(force_data_directory, exist_ok=True)
os.makedirs(ndi_data_directory, exist_ok=True)

force_data_filename = os.path.join(
    force_data_directory,
    f"sri_force-{current_time}.csv",
)
ndi_data_filename = os.path.join(
    ndi_data_directory,
    f"NDIdata_{current_time}.csv",
)

aurora_settings = {
    "tracker type": "aurora",
}

tracker = NDITracker(aurora_settings)
tracker._use_quaternions = True

initial_frame = pd.DataFrame(columns=["qx", "qy", "qz", "qw", "x", "y", "z"])
initial_frame.to_csv(ndi_data_filename, index=False)

# Initialize the SRI six-axis force/torque sensor.
sri_sensor_device = SRI_class.sunrise()
sri_sensor_device.enable()

# Shared shutdown flag for all threads.
exit_flag = False


def update_serial_with_falcon_position():
    """Read Falcon input and control translation stages and the puncture motor."""
    global button_states, velocity, exit_flag

    rotation_motor = MaxonMotor(
        5,
        b"EPOS2",
        b"MAXON SERIAL V2",
        b"USB",
        b"USB0",
        1000000,
    )
    rotation_motor.close_device()  # Close any previous device connection.
    rotation_motor.open_device()
    rotation_motor.set_max_acceleration(5000)
    rotation_motor.enable_device()

    # Initialize both serial ports.
    serial_connection_1 = serial.Serial(serial_port_1, baud_rate)
    print(f"Serial port {serial_port_1} connected successfully.")

    serial_connection_2 = serial.Serial(serial_port_2, baud_rate)
    print(f"Serial port {serial_port_2} connected successfully.")

    # Initialize the Falcon device.
    falcon_device = Falcon()
    falcon_device.open_device()

    # Read the initial position.
    current_position = falcon_device.get_cartesian_pos()
    current_feed_rate = 0.01

    # Apply resistance along the x-axis; units are defined by the Falcon driver.
    falcon_device.set_force(5, 0, 0)

    while not exit_flag:
        # Read Falcon button states and Cartesian velocity.
        button_states = falcon_device.get_button_states()
        velocity = falcon_device.get_cartesian_vel()
        previous_y_position = current_position[1]
        previous_z_position = current_position[0]

        time.sleep(0.0001)
        current_position = falcon_device.get_cartesian_pos()

        # Button 0: translate the upper stage.
        if button_states[0]:
            print(
                f"Button 0 pressed: sending upper-stage motion to "
                f"{serial_port_1} only."
            )
            current_y_position = current_position[1]
            current_z_position = current_position[0]
            y_change = current_y_position - previous_y_position
            z_change = current_z_position - previous_z_position

            x_command = 0.3 * y_change
            y_command = 0.3 * z_change
            z_command = 0

            output_message = (
                f"G91 G21 F{current_feed_rate:.2f} "
                f"X{x_command:.2f} Y{y_command:.2f} Z{z_command}\n"
            )
            serial_connection_1.write(output_message.encode("utf-8"))

        # Button 1: translate the lower stage.
        if button_states[1]:
            print(
                f"Button 1 pressed: sending lower-stage motion to "
                f"{serial_port_2} only."
            )
            current_y_position = current_position[1]
            current_z_position = current_position[0]
            y_change = current_y_position - previous_y_position
            z_change = current_z_position - previous_z_position

            x_command = 0.3 * y_change
            y_command = 0.3 * z_change
            z_command = 0

            output_message = (
                f"G91 G21 F{current_feed_rate:.2f} "
                f"X{-x_command:.2f} Y{-y_command:.2f} Z{z_command}\n"
            )
            serial_connection_2.write(output_message.encode("utf-8"))

        # Button 2: move the upper and lower stages together.
        elif button_states[2]:
            print(
                f"Button 2 pressed: sending coordinated motion to "
                f"{serial_port_1} and {serial_port_2}."
            )
            current_y_position = current_position[1]
            current_z_position = current_position[0]
            y_change = current_y_position - previous_y_position
            z_change = current_z_position - previous_z_position

            x_command = 0.3 * y_change
            y_command = 0.3 * z_change
            z_command = 0

            output_message_1 = (
                f"G91 G21 F{current_feed_rate:.2f} "
                f"X{x_command:.2f} Y{y_command:.2f} Z{z_command}\n"
            )
            output_message_2 = (
                f"G91 G21 F{current_feed_rate:.2f} "
                f"X{-x_command:.2f} Y{-y_command:.2f} Z{z_command}\n"
            )
            serial_connection_1.write(output_message_1.encode("utf-8"))
            serial_connection_2.write(output_message_2.encode("utf-8"))

        # Button 3: control the puncture rotation motor.
        if button_states[3]:
            rotation_motor.move_speed_mode(50 * int(-velocity[0]))
            print("Puncture motion active.")
        else:
            rotation_motor.move_speed_mode(0)

    # Shut down the motor, Falcon device, and serial ports.
    rotation_motor.disable_device()
    rotation_motor.close_device()
    falcon_device.close_device()
    serial_connection_1.close()
    serial_connection_2.close()
    sys.exit()


def collect_sri_sensor_data():
    """Collect SRI force/torque data and append it to a CSV file."""
    global exit_flag

    with open(force_data_filename, mode="a", newline="") as data_file:
        csv_writer = csv.writer(data_file)
        csv_writer.writerow(["Fx", "Fy", "Fz", "Mx", "My", "Mz"])

        while not exit_flag:
            force_data = sri_sensor_device.rec()

            # Calibration placeholder for future sensor correction factors.
            force_data[0] = force_data[0]
            force_data[1] = force_data[1]
            force_data[2] = force_data[2]
            force_data[3] = force_data[3]
            force_data[4] = force_data[4]
            force_data[5] = force_data[5]

            csv_writer.writerow(force_data[:6])
            print(f"SRI force data saved: {force_data[:6]}")
            time.sleep(0.01)

    sri_sensor_device.disable()
    print("SRI sensor disabled.")


def collect_ndi_tracking_data():
    """Collect NDI pose data and append it to a CSV file."""
    global exit_flag

    tracker.start_tracking()
    print("NDI tracking started. Press Esc to stop.")

    try:
        while not exit_flag:
            ndi_frame_data = tracker.get_frame()
            if ndi_frame_data and ndi_frame_data[3]:
                for tool_matrix in ndi_frame_data[3]:
                    if tool_matrix is not None:
                        matrix = np.array(tool_matrix)
                        position = matrix[0:3, 3]
                        rotation_matrix = matrix[0:3, 0:3]
                        quaternion = R.from_matrix(rotation_matrix).as_quat()
                        row = {
                            "x": position[0],
                            "y": position[1],
                            "z": position[2],
                            "qx": quaternion[0],
                            "qy": quaternion[1],
                            "qz": quaternion[2],
                            "qw": quaternion[3],
                        }
                        data_frame = pd.DataFrame([row])
                        data_frame.to_csv(
                            ndi_data_filename,
                            mode="a",
                            index=False,
                            header=False,
                        )
            time.sleep(0.01)
    except Exception as error:
        print("NDI tracking error:", error)
    finally:
        tracker.stop_tracking()
        tracker.close()
        print("NDI tracker stopped and closed.")


def listen_for_exit():
    """Monitor the Esc key and request a coordinated shutdown."""
    global exit_flag

    while not exit_flag:
        if keyboard.is_pressed("esc"):
            print("\nEsc pressed. Exiting...")
            exit_flag = True
            break
        time.sleep(0.0001)


if __name__ == "__main__":
    # Update these ports to match the entries shown in Windows Device Manager.
    serial_port_1 = "COM6"
    serial_port_2 = "COM7"
    baud_rate = 115200

    serial_control_thread = threading.Thread(
        target=update_serial_with_falcon_position,
    )
    serial_control_thread.start()

    sri_collection_thread = threading.Thread(
        target=collect_sri_sensor_data,
        daemon=True,
    )
    sri_collection_thread.start()

    ndi_collection_thread = threading.Thread(
        target=collect_ndi_tracking_data,
        daemon=True,
    )
    ndi_collection_thread.start()

    exit_listener_thread = threading.Thread(
        target=listen_for_exit,
        daemon=True,
    )
    exit_listener_thread.start()
