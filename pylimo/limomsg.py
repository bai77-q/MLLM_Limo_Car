from types import DynamicClassAttribute

def _init():
    global _global_dict
    _global_dict = {}



def SetValue(name, value):
    _global_dict[name] = value


def GetValue(name):
    return _global_dict.get(name, 0)

def SetLinearVelocity(linear_velocity):
    SetValue('linear_velocity', linear_velocity)


def GetLinearVelocity():
    return GetValue('linear_velocity')


def SetAngularVelocity(angular_velocity):
    SetValue('angular_velocity', angular_velocity)


def GetAngularVelocity():
    return GetValue('angular_velocity')


def SetLateralVelocity(lateral_velocity):
    SetValue('lateral_velocity', lateral_velocity)


def GetLateralVelocity():
    return GetValue('lateral_velocity')

def SetSteeringAngle(steering_angle):
    SetValue('steering_angle', steering_angle)


def GetSteeringAngle():
    return GetValue('steering_angle')

def SetVehicleState(vehicle_state):
    SetValue('vehicle_state', vehicle_state)

def GetVehicleState():
    return GetValue('vehicle_state')

def SetControlMode(control_mode):
    SetValue('control_mode', control_mode)

def GetControlMode():
    return GetValue('control_mode')

def SetBatteryVoltage(battery_voltage):
    SetValue('battery_voltage', battery_voltage)

def GetBatteryVoltage():
    return GetValue('battery_voltage')

def SetErrorCode(error_code):
    SetValue('error_code', error_code)

def GetErrorCode():
    return GetValue('error_code')

def SetLeftWheelOdom(left_wheel_odom):
    SetValue('left_wheel_odom', left_wheel_odom)

def GetLeftWheelOdom():
    return GetValue('left_wheel_odom')

def SetRightWheelOdom(right_wheel_odom):
    SetValue('right_wheel_odom', right_wheel_odom)

def GetRightWheelOdom():
    return GetValue('right_wheel_odom')

def SetIMUAccelX(IMU_accel_x):
    SetValue('IMU_accel_x', IMU_accel_x)

def GetIMUAccelX():
    return GetValue('IMU_accel_x')

def SetIMUAccelY(IMU_accel_y):
    SetValue('IMU_accel_y', IMU_accel_y)

def GetIMUAccelY():
    return GetValue('IMU_accel_y')

def SetIMUAccelZ(IMU_accel_z):
    SetValue('IMU_accel_z', IMU_accel_z)

def GetIMUAccelZ():
    return GetValue('IMU_accel_z')

def SetIMUGyroX(IMU_gyro_x):
    SetValue('IMU_gyro_x', IMU_gyro_x)

def GetIMUGyroX():
    return GetValue('IMU_gyro_x')

def SetIMUGyroY(IMU_gyro_y):
    SetValue('IMU_gyro_y', IMU_gyro_y)

def GetIMUGyroY():
    return GetValue('IMU_gyro_y')

def SetIMUGyroZ(IMU_gyro_z):
    SetValue('IMU_gyro_z', IMU_gyro_z)

def GetIMUGyroZ():
    return GetValue('IMU_gyro_z')

def SetIMUYaw(IMU_yaw):
    SetValue('IMU_yaw', IMU_yaw)

def GetIMUYaw():
    return GetValue('IMU_yaw')

def SetIMUPitch(IMU_pitch):
    SetValue('IMU_pitch', IMU_pitch)

def GetIMUPitch():
    return GetValue('IMU_pitch')

def SetIMURoll(IMU_roll):
    SetValue('IMU_roll', IMU_roll)

def GetIMURoll():
    return GetValue('IMU_roll')

def SetMotionMode(motion_mode):
    SetValue('motion_mode', motion_mode)

def GetMotionMode():
    return GetValue('motion_mode')

class LimoMsg(object):
    FRAME_HEADER = 0x55
    FRAME_LENGTH = 0x0E
    # /*--------------------------- Message IDs ------------------------------*/
    # // control group: 0x1
    MSG_MOTION_COMMAND_ID = 0x111
    # // state feedback group: 0x2
    MSG_SYSTEM_STATE_ID = 0x211
    MSG_MOTION_STATE_ID = 0x221

    MSG_ACTUATOR1_HS_STATE_ID = 0x251
    MSG_ACTUATOR2_HS_STATE_ID = 0x252
    MSG_ACTUATOR3_HS_STATE_ID = 0x253
    MSG_ACTUATOR4_HS_STATE_ID = 0x254

    MSG_ACTUATOR1_LS_STATE_ID = 0x261
    MSG_ACTUATOR2_LS_STATE_ID = 0x262
    MSG_ACTUATOR3_LS_STATE_ID = 0x263
    MSG_ACTUATOR4_LS_STATE_ID = 0x264

    # // sensor data group: 0x3
    MSG_ODOMETRY_ID = 0x311
    MSG_IMU_ACCEL_ID = 0x321
    MSG_IMU_GYRO_ID = 0x322
    MSG_IMU_EULER_ID = 0x323

    MSG_CTRL_MODE_CONFIG_ID = 0x421

    # def SerialFrame(self):
