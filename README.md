# Puncture Robot Control Programs

This repository provides two control programs for a research prototype of a
lung puncture robot. The programs are presented separately below so that their
different input devices and acquisition workflows are easy to identify.

## Programs at a Glance

| Program | Primary input | Motion control | Data acquisition | Default active workflow |
| --- | --- | --- | --- | --- |
| `Main_PunctureRobot_Force_NDI.py` | Falcon haptic device | Dual translation stages and Maxon puncture motor | SRI force/torque and NDI pose | Falcon control, SRI acquisition, and NDI tracking |
| `main_glove_force_NDI.py` | UDP data glove | No robot motion commands in this file | Data glove, SRI force/torque, and NDI position | SRI force acquisition only; glove and NDI threads are disabled by default |

---

# Program 1: Falcon Robot Control with Force and NDI Tracking

## 1. Overview

`Main_PunctureRobot_Force_NDI.py` is the main control program for a research
prototype of a lung puncture robot. It performs the following tasks:

1. Reads position, velocity, and button states from a Falcon device.
2. Sends G-code motion commands to upper and lower translation stages through
   two serial ports.
3. Controls a Maxon puncture rotation motor.
4. Records six-axis force/torque data from an SRI sensor.
5. Records pose data from an NDI Aurora tracking system.
6. Stops data acquisition when the Esc key is pressed.

## 2. Public Release Scope

This program documents the Falcon-based robot control workflow. Vendor SDKs,
device drivers, calibration files, and project-specific hardware support may
be required in addition to the files in this repository.

Consequently, the program cannot run on a standard computer without the
required hardware and licensed software environment.

## 3. Environment

Recommended environment:

- 64-bit Windows
- Python 3
- Properly installed and connected Falcon, Maxon, SRI, and NDI Aurora devices

Required third-party Python packages:

- pyserial
- keyboard
- pandas
- numpy
- scipy
- scikit-surgerynditracker and its runtime dependencies

The hardware environment also requires these local modules or equivalent
implementations:

- `SRI_class.py`
- `maxon_core.py`
- `Falcon_dll.py`

The hardware layer requires the corresponding vendor libraries, including the
Falcon driver library and Maxon EPOS command library. Do not publish vendor
files unless their licenses explicitly permit redistribution.

## 4. Configuration

Before running the program:

1. Find the two motion-controller COM ports in Windows Device Manager.
2. Open `Main_PunctureRobot_Force_NDI.py` and update the following settings in
   the main entry point:

   ```python
   serial_port_1 = "COM6"
   serial_port_2 = "COM7"
   ```

3. Confirm that the baud rate matches both controllers. The default value is
   115200.
4. Verify that the NDI Aurora tracker, SRI sensor, Falcon device, and Maxon
   motor are connected and configured correctly.
5. Ensure that the local wrapper modules and vendor libraries are available to
   Python at runtime.

## 5. Running the Program

In a fully configured hardware environment, run:

```text
python Main_PunctureRobot_Force_NDI.py
```

The program creates two output directories beside the source file:

- `Force_NDI_data`: SRI force/torque CSV files
- `result`: NDI pose CSV files

Press Esc to request shutdown of all acquisition threads.

## 6. Data Fields

SRI force/torque data:

- `Fx`, `Fy`, `Fz`: force components along three axes
- `Mx`, `My`, `Mz`: moment components about three axes

NDI pose data:

- `x`, `y`, `z`: position components
- `qx`, `qy`, `qz`, `qw`: orientation quaternion components

---

# Program 2: Data Glove, Force, and NDI Acquisition

## 1. Overview

`main_glove_force_NDI.py` is an experimental data-acquisition program that
combines three possible input streams:

1. UDP data-glove measurements in JSON format.
2. Six-axis force/torque measurements from an SRI sensor.
3. Position measurements from an NDI Aurora tracking system.

This file records sensor data only. It does not send the dual-stage G-code or
Maxon motor commands used by Program 1.

## 2. Default Behavior

In the released configuration, the SRI force-acquisition thread is enabled.
The NDI and data-glove thread creation and startup lines are commented out.
The UDP data-glove configuration block is also commented out.

The program still initializes the NDI tracker and SRI sensor in its main entry
point. Pressing Esc sets the three stop flags and requests program shutdown.

## 3. Environment

Recommended environment:

- 64-bit Windows
- Python 3
- An SRI six-axis force/torque sensor
- An NDI Aurora tracking system when NDI acquisition is enabled
- A UDP data-glove source when glove acquisition is enabled

Required third-party Python packages:

- keyboard
- pandas
- numpy
- scikit-surgerynditracker and its runtime dependencies

The program also requires `SRI_class.py` or an equivalent implementation.

## 4. Optional UDP Data-Glove Configuration

Before enabling glove acquisition, review and uncomment the configuration block
near the top of `main_glove_force_NDI.py`:

```python
HOST = "127.0.0.1"
PORT = 5555
BUFSIZ = 10240
ADDR = (HOST, PORT)
UDPCliSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
target_names = [f"l{i}" for i in range(28)] + [f"r{i}" for i in range(28)]
csv_columns = target_names
csv_glove_name = "./result/Glovedata_" + now + ".csv"
```

The expected JSON payload contains a `Device1_5555` object with a `Parameter`
list. Each selected parameter must provide `Name` and `Value` fields. Adjust
the host, port, device key, and target parameter names to match the actual
glove data source.

To activate the optional streams, uncomment their thread creation and startup
lines only after the associated hardware and configuration are ready:

```python
NDI_thread = threading.Thread(target=NDI_track)
Glove_thread = threading.Thread(target=Glove)
NDI_thread.start()
Glove_thread.start()
```

## 5. Running the Program

In a fully configured hardware environment, run:

```text
python main_glove_force_NDI.py
```

The program creates a `result` directory in the current working directory.
Depending on the enabled acquisition threads, it can produce:

- `Forcedata_<timestamp>.csv`: SRI force/torque data
- `NDIdata_<timestamp>.csv`: NDI position data
- `Glovedata_<timestamp>.csv`: UDP data-glove parameters

## 6. Data Fields

SRI force/torque data:

- `Fx`, `Fy`, `Fz`: force components along three axes
- `Tx`, `Ty`, `Tz`: torque components about three axes

NDI data:

- `x1`, `y1`, `z1`: tracked position components

Data-glove data:

- `l0` through `l27`: left-glove parameters
- `r0` through `r27`: right-glove parameters

---

## Safety Notice

These programs interact with physical robotic and sensing hardware. Before
operation, verify mechanical limits, emergency-stop functionality, speed
limits, collision risks, sensor connections, and serial-port assignments.
Operation must be supervised by personnel familiar with the system and
performed in a controlled research environment.

The source code is provided for research and technical communication only. It
is not approved for clinical diagnosis, clinical treatment, or unsupervised
human-subject experiments.
