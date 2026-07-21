Force-Guided and NDI-Tracked Lung Puncture Robot
================================================

1. Overview
-----------

Main_PunctureRobot_Force_NDI.py is the main control program for a research
prototype of a lung puncture robot. It performs the following tasks:

1. Reads position, velocity, and button states from a Falcon device.
2. Sends G-code motion commands to upper and lower translation stages through
   two serial ports.
3. Controls a Maxon puncture rotation motor.
4. Records six-axis force/torque data from an SRI sensor.
5. Records pose data from an NDI Aurora tracking system.
6. Stops data acquisition when the Esc key is pressed.

2. Public Release Scope
-----------------------

This folder contains only the main source file and this documentation. It does
not include vendor SDKs, dynamic-link libraries, device drivers, calibration
files, experimental data, or project-specific hardware wrapper modules.

Consequently, this repository is intended to document the control workflow and
cannot run on a standard computer without the required hardware and licensed
software environment.

3. Environment
--------------

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

The original hardware environment also requires these local modules or
equivalent implementations:

- SRI_class.py
- maxon_core.py
- Falcon_dll.py

The hardware layer requires the corresponding vendor libraries, including the
Falcon driver library and Maxon EPOS command library. Do not publish vendor
files unless their licenses explicitly permit redistribution.

4. Configuration
----------------

Before running the program:

1. Find the two motion-controller COM ports in Windows Device Manager.
2. Open Main_PunctureRobot_Force_NDI.py and update the following settings in
   the main entry point:

       serial_port_1 = "COM6"
       serial_port_2 = "COM7"

3. Confirm that the baud rate matches both controllers. The default value is
   115200.
4. Verify that the NDI Aurora tracker, SRI sensor, Falcon device, and Maxon
   motor are connected and configured correctly.
5. Ensure that the local wrapper modules and vendor libraries are available to
   Python at runtime.

5. Running the Program
----------------------

In a fully configured hardware environment, run:

    python Main_PunctureRobot_Force_NDI.py

The program creates two output directories beside the source file:

- Force_NDI_data: SRI force/torque CSV files
- result: NDI pose CSV files

Press Esc to request shutdown of all acquisition threads.

6. Data Fields
--------------

SRI force/torque data:

- Fx, Fy, Fz: force components along three axes
- Mx, My, Mz: moment components about three axes

NDI pose data:

- x, y, z: position components
- qx, qy, qz, qw: orientation quaternion components

7. Safety Notice
----------------

This software controls physical robotic hardware and an electric motor. Before
operation, verify mechanical limits, emergency-stop functionality, speed
limits, collision risks, and serial-port assignments. Operation must be
supervised by personnel familiar with the system and performed in a controlled
research environment.

This source code is provided for research and technical communication only. It
is not approved for clinical diagnosis, clinical treatment, or unsupervised
human-subject experiments.

8. GitHub Upload Checklist
--------------------------

Upload only these two files from this folder:

- Main_PunctureRobot_Force_NDI.py
- readme.txt

Before making the repository public, verify that it contains no patient data,
experimental records, credentials, API keys, proprietary SDKs, or restricted
vendor libraries.
