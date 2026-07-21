"""This module includes core functions of maxon motor.
Class: MaxonMotor
"""

from ctypes import *
BOOL = c_int
DWORD = c_ulong
HANDLE = c_void_p
UINT = c_uint
CHAR = c_char_p
USHORT = c_ushort
LONG = c_long
INT = c_int
SHORT = c_short
WORD = c_ushort


class MaxonMotor(object):
    def __init__(self, node_id, device_name, protocol_stack_name, interface_name, port_name, baud_rate):
        self.maxon_motor_dll = cdll.LoadLibrary("machine_language_driver/EposCmd64.dll")  #windows的库函数
        # Initialize parameters
        self.node_id = USHORT(node_id)
        self.device_name = CHAR(device_name)
        self.protocol_stack_name = CHAR(protocol_stack_name)
        self.interface_name = CHAR(interface_name)
        self.port_name = CHAR(port_name)
        self.baud_rate = UINT(baud_rate)
        self.handle = HANDLE(0)
        self.error_code = UINT(0)
        self.time_out = UINT(0)
        # Runtime parameters
        self.motor_position = LONG(0)
        self.motor_velocity = LONG(0)
        self.motor_current = SHORT(0)
        self.motor_move_state = BOOL(0)
        self.motion_mode = None  # 'P' - position mode; 'A' - current mode; 'V' - velocity mode
        self.analog_input_1 = INT(0)  # analog input 1
        self.analog_input_2 = INT(0)  # analog input 2
        self.digital_input_1 = c_uint(0)  # digital input 1

    def set_max_acceleration(self, max_acceleration):
        """
        Safety parameter. Set the maximal acceleration/deceleration.
        :param max_acceleration: maximal value, unit rpm/s
        :return:True on success, False otherwise
        """
        if self.maxon_motor_dll.VCS_SetMaxAcceleration(self.handle, self.node_id, DWORD(max_acceleration),
                                                       byref(self.error_code)) != BOOL(0):
            return True
        else:
            return False

    def open_device(self):
        """
        Open the maxon motor, but not enable it.

        :return: True on success, False otherwise
        """
        print("Opening maxon device...")
        self.handle = self.maxon_motor_dll.VCS_OpenDevice(self.device_name, self.protocol_stack_name,
                                                          self.interface_name, self.port_name, byref(self.error_code))
        if self.handle == 0:
            print('Open maxon device failed!')
            print('Error: ' + str(self.error_code.value))
            return False
        else:
            print('Success!')
            return True

    def enable_device(self):
        """
        Clear the fault state, then enable the motor.

        :return: True on success, False otherwise
        """
        self.maxon_motor_dll.VCS_ClearFault(self.handle, self.node_id, byref(self.error_code))
        if self.maxon_motor_dll.VCS_SetEnableState(self.handle, self.node_id, byref(self.error_code)) == BOOL(0):
            return False
        else:
            return True

    def current_mode(self, current_value):
        """
        Activate current mode and set the current value(unit: mA)

        :param current_value: demanded current value(unit: mA)
        :return: True on success, False otherwise
        C date: 2019/8/30
        M date: 2019/9/15
        """
        is_success = False
        if self.maxon_motor_dll.VCS_ActivateCurrentMode(self.handle, self.node_id, byref(self.error_code)) != BOOL(0):
            self.motion_mode = 'A'
            if self.maxon_motor_dll.VCS_SetCurrentMust(self.handle,
                                                       self.node_id,
                                                       SHORT(current_value),
                                                       byref(self.error_code)) != BOOL(0):
                is_success = True
        return is_success

    def activate_profile_velocity_mode(self):
        """
        Activate profile speed mode.
        unit: rpm
        :return: None
        """
        if self.maxon_motor_dll.VCS_ActivateProfileVelocityMode(self.handle,
                                                                self.node_id,
                                                                byref(self.error_code)) != BOOL(0):
            self.motion_mode = 'V'

    def move_speed_mode(self, target_velocity):
        """
        Move with demanded velocity.

        :param target_velocity: Unit - rpm
        :return: True on success, False otherwise
        """
        if self.motion_mode != 'V':
            self.activate_profile_velocity_mode()
        if self.maxon_motor_dll.VCS_MoveWithVelocity(self.handle, self.node_id,
                                                     LONG(target_velocity), byref(self.error_code)) != BOOL(0):
            return True
        else:
            return False

    def move_to_position(self, position_mode_speed, target_position, is_absolute=1, is_immediate=1):
        """
        Activate profile position mode, then move to demanded position.

        :param position_mode_speed: set profile speed (unit: rpm)
        :param target_position: set target position (Default: 2000qc/turn)
        :param is_absolute: 1 - move absolute position; 0 - move relative position
        :param is_immediate: 1 - move immediately; 0 - waits to end of last positioning
        :return: True on success, False otherwise
        """
        acceleration = UINT(100000)
        deceleration = UINT(100000)
        self.maxon_motor_dll.VCS_ActivateProfilePositionMode(self.handle, self.node_id, byref(self.error_code))
        self.maxon_motor_dll.VCS_SetPositionProfile(self.handle, self.node_id, UINT(position_mode_speed),
                                                    acceleration, deceleration, byref(self.error_code))
        self.motion_mode = 'P'
        if self.maxon_motor_dll.VCS_MoveToPosition(self.handle, self.node_id, LONG(target_position), INT(is_absolute),
                                                   INT(is_immediate), byref(self.error_code)) == BOOL(0):
            return False
        else:
            return True

    def activate_homing_mode(self):
        """
              Activate homing mode.
              :return: None
              """
        if self.maxon_motor_dll.VCS_ActivateHomingMode(self.handle,self.node_id,
                                                                byref(self.error_code)) != BOOL(0):
            self.motion_mode = 'V'

    def define_position(self,homing_position):
        if self.motion_mode != 'V':
            self.activate_profile_velocity_mode()
        if self.maxon_motor_dll.VCS_DefinePosition(self.handle, self.node_id, LONG(homing_position),
                                                   byref(self.error_code)) == BOOL(0):
            return False
        else:
            return True

    def wait_for_target_reached(self, time_out=100000):
        """
        Waits until the state is changed to target reached or until the time is up.

        :param time_out: timeout
        :return: True on success, False otherwise
        """
        if self.maxon_motor_dll.VCS_WaitForTargetReached(self.handle, self.node_id,
                                                         UINT(time_out), byref(self.error_code)) == BOOL(0):
            return False
        else:
            return True

    def is_target_reached(self):
        """
        Checks if the drive has reached target.

        :return: True on success, False otherwise
        """
        self.maxon_motor_dll.VCS_GetMovementState(self.handle, self.node_id, byref(self.motor_move_state),
                                                  byref(self.error_code))
        if self.motor_move_state.value == 0:
            return False
        else:
            return True

    def get_rt_position(self):
        """
        Get realtime position
        :return: motor position, unit - qc
        """
        if self.maxon_motor_dll.VCS_GetPositionIs(self.handle, self.node_id,
                                                  byref(self.motor_position), byref(self.error_code)) != BOOL(0):
            return self.motor_position.value

    def get_rt_velocity(self):
        """
        Get realtime velocity.
        :return:  motor velocity, unit - rpm
        """
        if self.maxon_motor_dll.VCS_GetVelocityIs(self.handle, self.node_id,
                                                  byref(self.motor_velocity), byref(self.error_code)) != BOOL(0):
            return self.motor_velocity.value

    def get_rt_current(self):
        """
        Get realtime current value.
        :return:  motor current, unit - mA
        """
        if self.maxon_motor_dll.VCS_GetCurrentIs(self.handle, self.node_id,
                                                 byref(self.motor_current), byref(self.error_code)) != BOOL(0):
            return self.motor_current.value

    def get_analog_input_1(self):
        """
        Get realtime analog signal input of Input 1.
        :return: analog signal input 1
        """
        if self.maxon_motor_dll.VCS_GetAnalogInput(self.handle, self.node_id, 1,
                                                   byref(self.analog_input_1),
                                                   byref(self.error_code)) != BOOL(0):
            return self.analog_input_1.value

    def get_analog_input_2(self):
        """
        Get realtime analog signal input of Input 2.
        :return: analog signal input 2
        """
        if self.maxon_motor_dll.VCS_GetAnalogInput(self.handle, self.node_id, 2,
                                                   byref(self.analog_input_2),
                                                   byref(self.error_code)) != BOOL(0):
            return self.analog_input_2.value

    def get_digital_input_1(self):
        """
        Get realtime digital signal input of Input 1.
        :return: digital signal input 1
        """

        if self.maxon_motor_dll.VCS_GetAllDigitalInputs(self.handle, self.node_id,
                                                        byref(self.digital_input_1),
                                                        byref(self.error_code)) != BOOL(0):
            return self.digital_input_1.value

    def update_runtime_param(self):
        """
        Update the runtime position, velocity and current of motor.

        :return: True on success, False otherwise
        """
        is_success = False
        if self.maxon_motor_dll.VCS_GetPositionIs(self.handle, self.node_id,
                                                  byref(self.motor_position), byref(self.error_code)) != BOOL(0):
            if self.maxon_motor_dll.VCS_GetVelocityIs(self.handle, self.node_id,
                                                      byref(self.motor_velocity), byref(self.error_code)) != BOOL(0):
                if self.maxon_motor_dll.VCS_GetCurrentIs(self.handle, self.node_id,
                                                         byref(self.motor_current), byref(self.error_code)) != BOOL(0):
                    is_success = True
        return is_success

    def disable_device(self):
        """
        Changes the device state to “disable”.

        :return: True on success, False otherwise
        """
        if self.maxon_motor_dll.VCS_SetDisableState(self.handle, self.node_id, byref(self.error_code)) != BOOL(0):
            self.motion_mode = None
            return True
        else:
            return False

    def close_device(self):
        """
        Close port.

        :return: True on success, False otherwise
        """
        if self.maxon_motor_dll.VCS_CloseDevice(self.handle, byref(self.error_code)) != BOOL(0):
            print('Close maxon device successfully!')
            self.motion_mode = None
            return True
        else:
            return False

    def stop(self):
        self.maxon_motor_dll.VCS_QuickStop(self.handle, self.node_id, byref(self.error_code))
        self.motion_mode = None

    def halt_velocity(self):
        self.maxon_motor_dll.VCS_HaltVelocityMovement(self.handle, self.node_id, byref(self.error_code))
        self.enable_device()
        self.motion_mode = None

    def halt_position(self):
        self.maxon_motor_dll.VCS_HaltPositionMovement(self.handle, self.node_id, byref(self.error_code))
        self.enable_device()
        self.motion_mode = None
