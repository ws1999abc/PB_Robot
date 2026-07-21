import csv
import json
import os
import socket
import sys
import threading
import time
from datetime import datetime

import keyboard
import numpy as np
import pandas as pd
from sksurgerynditracker.nditracker import NDITracker

from SRI_class import sunrise  # Custom SRI class expected in the same directory.


# Define global state.
stop_event = threading.Event()
save_folder = "result"
os.makedirs(save_folder, exist_ok=True)
stop_force_flag = False
stop_NDI_flag = False
stop_Glove_flag = False
now = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))


force_filename = "./result/Forcedata_" + now + ".csv"
frame = pd.DataFrame(columns=["Fx", "Fy", "Fz", "Tx", "Ty", "Tz"])
frame.to_csv(force_filename, index=False)

ndi_filename = "./result/NDIdata_" + now + ".csv"
frame = pd.DataFrame(columns=["x1", "y1", "z1"])
frame.to_csv(ndi_filename, index=False)


def NDI_track():
    global stop_NDI_flag
    # print(TRACKER.get_tool_descriptions())
    while not stop_NDI_flag:
        # print(TRACKER.get_frame())
        time.sleep(0.01)
        ndi_data = TRACKER.get_frame()
        new_ndi_list = []
        for i in range(len(ndi_data[3])):  # Number of data items.
            for j in range(len(ndi_data)):  # Number of ports.
                if j == 1:
                    pass
                elif j == 3:
                    # tracking_list = ndi_data[j][i].tolist()[0]
                    # Read the x, y, and z translation components.
                    tracking_list = [x[3] for x in ndi_data[j][i].tolist()]
                    if tracking_list:
                        for k in range(len(tracking_list) - 1):
                            new_ndi_list.append(tracking_list[k])
                        new_ndi_list = [x for x in new_ndi_list if not np.isnan(x)]
                        if new_ndi_list and len(new_ndi_list) == 3:
                            print(new_ndi_list)
                            ndi = pd.DataFrame(columns=new_ndi_list)
                            ndi.to_csv(ndi_filename, index=False, mode="a")
                else:
                    pass

    TRACKER.stop_tracking()
    TRACKER.close()


# UDP data-glove configuration. Uncomment this block before enabling the glove
# acquisition thread, and update the address and data fields if required.
HOST = "127.0.0.1"
PORT = 5555
BUFSIZ = 10240
ADDR = (HOST, PORT)
print(ADDR)
UDPCliSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
target_names = [f"l{i}" for i in range(28)] + [f"r{i}" for i in range(28)]
csv_columns = target_names
csv_glove_name = "./result/Glovedata_" + now + ".csv"


def Glove():
    global stop_Glove_flag
    try:
        with open(csv_glove_name, "w", newline="") as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
            csv_writer.writeheader()
            UDPCliSock.bind(ADDR)

            while not stop_Glove_flag:
                # Listen for UDP data.
                data, addr = UDPCliSock.recvfrom(BUFSIZ)
                try:
                    received_data = json.loads(data.decode("utf-8"))
                    if "Device1_5555" in received_data:
                        device_data = received_data["Device1_5555"]
                        if "Parameter" in device_data:
                            parameter_data = device_data["Parameter"]
                            row_data = {name: None for name in csv_columns}

                            for item in parameter_data:
                                if "Name" in item and "Value" in item:
                                    name = item["Name"]
                                    if name in target_names:
                                        print(f'Value for "{name}": {item["Value"]}')
                                        row_data[name] = item["Value"]

                            csv_writer.writerow(row_data)
                            time.sleep(0.02)

                except json.JSONDecodeError:
                    print("Received data is not valid JSON.")

                # Stop when the Esc key is pressed.
                if keyboard.is_pressed("esc"):
                    break

    except Exception as error:
        print("UDP reception failed. Error details are shown below:")
        print(error)
        input("Press Enter to exit.")

    finally:
        UDPCliSock.close()  # Close the client socket.


def force():
    global stop_force_flag
    with open(force_filename, "a", newline="") as file:
        writer = csv.writer(file)
        # writer.writerow(data)
        while not stop_force_flag:
            F = SRI.rec()
            # F = [float(x) for x in F]
            Fx = F[0]
            Fy = F[1]
            Fz = F[2]
            Tx = F[3]
            Ty = F[4]
            Tz = F[5]
            F_tri = [Fx, Fy, Fz, Tx, Ty, Tz]
            print(F_tri)
            writer.writerow(F_tri)
            time.sleep(0.01)

        SRI.disable()


def finish():
    global stop_NDI_flag, stop_Glove_flag, stop_force_flag
    stop_NDI_flag = True
    stop_Glove_flag = True
    stop_force_flag = True


def on_esc_press(event):
    if event.name == "esc":
        print("Program stopped.")
        finish()
        UDPCliSock.close()
        sys.exit()


if __name__ == "__main__":
    settings_aurora = {
        "tracker type": "aurora",
    }

    TRACKER = NDITracker(settings_aurora)
    TRACKER._use_quaternions = True
    TRACKER.start_tracking()
    SRI = sunrise()
    SRI.enable()

    import threading

    NDI_thread = threading.Thread(target=NDI_track)
    Glove_thread = threading.Thread(target=Glove)
    Force_thread = threading.Thread(target=force)
    NDI_thread.start()
    Glove_thread.start()
    Force_thread.start()
    keyboard.on_press(on_esc_press)
