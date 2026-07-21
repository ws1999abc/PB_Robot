Puncture Robot Control Programs
===============================

This repository contains two Python programs used for a research prototype of a percutaneous biopsy robot. The code is provided for academic research and technical communication.

Program List
------------

Program 1:
File: Main_PunctureRobot_Force_NDI.py
Main function: Falcon-based robot control with SRI force sensing and NDI tracking.

Program 2:
File: main_glove_force_NDI.py
Main function: Data acquisition from a data glove, SRI force sensor, and NDI tracking system.


Program 1: Falcon-Based Robot Control
-------------------------------------

Overview

Main_PunctureRobot_Force_NDI.py is the main control program for the lung puncture robot prototype.

This program performs Falcon-based leader control, controls two translation stages through serial ports, drives a Maxon puncture motor, and records SRI force/torque data and NDI pose data.

Main Functions

- Read position, velocity, and button states from a Falcon haptic device.
- Control upper and lower translation stages through serial ports.
- Control a Maxon EPOS motor for puncture motion.
- Record six-axis force/torque data from an SRI sensor.
- Record pose data from an NDI Aurora tracking system.
- Save experimental data as CSV files.
- Stop the program by pressing the Esc key.

Output Data

The program creates the following output folders:

Force_NDI_data/
result/

SRI force/torque data include:

Fx, Fy, Fz, Mx, My, Mz

NDI pose data include:

x, y, z, qx, qy, qz, qw

Running Program 1

Before running the program, check and update the serial ports in the code if needed:

serial_port_1 = "COM6"
serial_port_2 = "COM7"

Run the program using:

python Main_PunctureRobot_Force_NDI.py


Program 2: Data Glove, Force, and NDI Acquisition
-------------------------------------------------

Overview

main_glove_force_NDI.py is an experimental data-acquisition program.

This program is used to collect multimodal data from a UDP data glove, an SRI six-axis force/torque sensor, and an NDI Aurora tracking system.

Unlike Program 1, this file does not send robot motion commands to the translation stages or the Maxon motor. It is mainly used for sensor data acquisition.

Main Functions

- Receive UDP data-glove signals.
- Record SRI six-axis force/torque data.
- Record NDI tracking data.
- Save glove, force, and NDI data as CSV files.
- Stop data acquisition by pressing the Esc key.

Default Behavior

In the released version, SRI force acquisition is enabled by default.

The data-glove and NDI acquisition threads are disabled by default and can be enabled by uncommenting the corresponding lines in the code.

Output Data

Depending on the enabled acquisition threads, the program can generate:

Forcedata_<timestamp>.csv
NDIdata_<timestamp>.csv
Glovedata_<timestamp>.csv

SRI force/torque data include:

Fx, Fy, Fz, Tx, Ty, Tz

NDI data include:

x1, y1, z1

Data-glove data include:

l0-l27, r0-r27

Running Program 2

Run the program using:

python main_glove_force_NDI.py


Requirements
------------

Recommended Environment

- Windows 64-bit.
- Python 3.
- Falcon haptic device.
- SRI six-axis force/torque sensor.
- NDI Aurora tracking system.
- Maxon EPOS motor controller.
- UDP data glove source.

Required Python Packages

- numpy
- pandas
- keyboard
- pyserial
- scipy
- scikit-surgerynditracker

Local Hardware Modules

The programs require the following local hardware interface modules or equivalent implementations:

- SRI_class.py
- maxon_core.py
- Falcon_dll.py

