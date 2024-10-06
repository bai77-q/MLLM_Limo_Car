#!/usr/bin/env python3
# codeing =utf-8
import os
import sys
import serial
import time
import ctypes
import threading
import asyncio
import math
import pylimo.limomsg as limomsg

import serial.tools.list_ports

from typing import Optional
port_list = list(serial.tools.list_ports.comports())


class LimoSerial:
    def __init__(self, name=None, baudrate=None):
        limomsg._init()
        if name == None:
            name = "/dev/ttyTHS0"
        elif len(port_list) == 0:
            print('no serial')
            # else serial.
        if baudrate == None:
            baudrate = "460800"
        self.serial_port = serial.Serial(name, baudrate, timeout=0.1)
        self.motion_mode = 0
        self.left_angle_scale_=2.47
        self.right_angle_scale_ = 1.64
        self.use_mcnamu = False
        with serial.Serial(name, baudrate, timeout=0.1) as receiver:
            serial_receive = threading.Thread(target=self.EnableAsynsSerial)
            serial_receive.start()
        time.sleep(0.2)

    def EnableAsynsSerial(self):

        while True:
            self.LimoGetFrame()

    def LimoSerialWrite(self, frame):
        write_data = [0]*limomsg.LimoMsg.FRAME_LENGTH
        write_data[0] = limomsg.LimoMsg.FRAME_HEADER
        write_data[1] = limomsg.LimoMsg.FRAME_LENGTH
        write_data[2] = (frame.port_id >> 8)
        write_data[3] = (frame.port_id & 0xff)
        write_num = 0

        write_checksum = 0
        # print('frame.port_id%s'%frame.port_id)
        for write_num in range(8):
            write_data[write_num + 4] = frame.data[write_num]
            write_checksum += frame.data[write_num]

        write_data[14 - 1] = ((write_checksum % 256) & 0xff)

        # port_->writeData(data, frame_len);
        self.serial_port.write(write_data)
        #self.log.debug("_write: {}".format(date))
        # self.serial_port.write(date)
        self.serial_port.flush()
        time.sleep(0.001)

    def LimoSerialRead(self):

        if self.serial_port.in_waiting:
            read_data = self.serial_port.read(limomsg.LimoMsg.FRAME_LENGTH*2)

            if read_data[read_data.index(limomsg.LimoMsg.FRAME_HEADER)+limomsg.LimoMsg.FRAME_LENGTH] == limomsg.LimoMsg.FRAME_HEADER:
                data = read_data[read_data.index(
                    limomsg.LimoMsg.FRAME_HEADER):read_data.index(limomsg.LimoMsg.FRAME_HEADER)+limomsg.LimoMsg.FRAME_LENGTH]

            else:
                data = []

        else:
            data = []
        return data

    def LimoGetFrame(self):
        read_frame = LimoFrame()
        data = self.LimoSerialRead()
        if not data:
            return []
        read_frame.port_id = (data[2] << 8) | data[3]
        data_num = 0
        checksum = 0
        for data_num in range(8):
            read_frame.data[data_num] = data[data_num+4]
            checksum += data[data_num+4]

        if data[13] == (checksum % 256):
            self.ParseFrame(read_frame)
        else:
            print('Invalid frame! Check sum failed!')

    def ParseFrame(self, frame):
        if(frame.port_id == limomsg.LimoMsg.MSG_MOTION_STATE_ID):

            linear_velocity_get = ctypes.c_int16((frame.data[0] & 0xff) << 8
                                                 | frame.data[1])
            linear_velocity = float(linear_velocity_get.value / 1000)
            limomsg.SetLinearVelocity(linear_velocity)
            angular_velocity_get = ctypes.c_int16((frame.data[2] & 0xff) << 8
                                                  | frame.data[3])
            angular_velocity = float(angular_velocity_get.value / 1000)
            limomsg.SetAngularVelocity(angular_velocity)
            lateral_velocity_get = ctypes.c_int16((frame.data[4] & 0xff) << 8
                                                  | frame.data[5])
            lateral_velocity = float(lateral_velocity_get.value / 1000)
            limomsg.SetLateralVelocity(lateral_velocity)
            steering_angle_get = ctypes.c_int16((frame.data[6] & 0xff) << 8
                                                | frame.data[7])
            steering_angle = float(steering_angle_get.value / 1000)
            if (steering_angle > 0) :
                steering_angle *= self.left_angle_scale_
            
            else :
                steering_angle *= self.right_angle_scale_
            
            limomsg.SetSteeringAngle(steering_angle)
            #print('linear_velocity:%s angular_velocity:%s' % (linear_velocity,angular_velocity))
        elif(frame.port_id == limomsg.LimoMsg.MSG_SYSTEM_STATE_ID):
            vehicle_state = frame.data[0]
            limomsg.SetVehicleState(vehicle_state)
            control_mode = frame.data[1]
            limomsg.SetControlMode(control_mode)
            battery_voltage = float(
                (frame.data[3] & 0xff) | (frame.data[2] << 8)) * 0.1
            limomsg.SetBatteryVoltage(battery_voltage)
            error_code = ((frame.data[5] & 0xff) | (frame.data[4] << 8))
            limomsg.SetErrorCode(error_code)
            if not self.use_mcnamu:
                motion_mode = frame.data[6]
                limomsg.SetMotionMode(motion_mode)

            self.ProcessErrorCode(error_code)
            # print('vehicle_state:%s'%(motion_mode))
            #print('vehicle_state:%s control_mode: %s battery_voltage: %s error_code:%s' %(vehicle_state,control_mode,battery_voltage,error_code))
        elif (frame.port_id == limomsg.LimoMsg.MSG_ODOMETRY_ID):
            left_wheel_odom_get = ctypes.c_int((frame.data[3] & 0xff) | (
                frame.data[2] << 8) | (frame.data[1] << 16) | (frame.data[0] << 24))
            left_wheel_odom = left_wheel_odom_get.value
            limomsg.SetLeftWheelOdom(left_wheel_odom)
            right_wheel_odom_get = ctypes.c_int((frame.data[7] & 0xff) | (
                frame.data[6] << 8) | (frame.data[5] << 16) | (frame.data[4] << 24))
            right_wheel_odom = right_wheel_odom_get.value
            limomsg.SetRightWheelOdom(right_wheel_odom)
            #print('left_wheel_odom:%s right_wheel_odom:%s' %(left_wheel_odom,right_wheel_odom))
        elif(frame.port_id == limomsg.LimoMsg.MSG_IMU_ACCEL_ID):
            imu_accel_x = ((frame.data[1] & 0xff) |
                           (frame.data[0] << 8)) / 100.0
            limomsg.SetIMUAccelX(imu_accel_x)
            imu_accel_y = ((frame.data[3] & 0xff) |
                           (frame.data[2] << 8)) / 100.0
            limomsg.SetIMUAccelY(imu_accel_y)
            imu_accel_z = ((frame.data[5] & 0xff) |
                           (frame.data[4] << 8)) / 100.0
            limomsg.SetIMUAccelZ(imu_accel_z)
            #print('imu_accel_x:%s imu_accel_y:%s imu_accel_z:%s' %(imu_accel_x,imu_accel_y,imu_accel_z))
        elif(frame.port_id == limomsg.LimoMsg.MSG_IMU_GYRO_ID):
            imu_gyro_x = (((frame.data[1] & 0xff) |
                          (frame.data[0] << 8)) / 100.0)
            limomsg.SetIMUGyroX(imu_gyro_x)
            imu_gyro_y = (((frame.data[3] & 0xff) |
                          (frame.data[2] << 8)) / 100.0)
            limomsg.SetIMUGyroY(imu_gyro_y)
            imu_gyro_z = (((frame.data[5] & 0xff) |
                          (frame.data[4] << 8)) / 100.0)
            limomsg.SetIMUGyroZ(imu_gyro_z)
            #print('imu_gyro_x:%s imu_gyro_y:%s imu_gyro_z:%s' %(imu_gyro_x,imu_gyro_y,imu_gyro_z))
        elif(frame.port_id == limomsg.LimoMsg.MSG_IMU_EULER_ID):
            imu_yaw = ((frame.data[1] & 0xff) | (frame.data[0] << 8)) / 100.0
            limomsg.SetIMUYaw(imu_yaw)
            imu_pitch = ((frame.data[3] & 0xff) | (frame.data[2] << 8)) / 100.0
            limomsg.SetIMUPitch(imu_pitch)
            imu_roll = ((frame.data[5] & 0xff) | (frame.data[4] << 8)) / 100.0
            limomsg.SetIMURoll(imu_roll)
            #print('imu_yaw:%s imu_pitch:%s imu_roll:%s' %(imu_yaw,imu_pitch,imu_roll))
        # elif(frame.port_id==limomsg.LimoMsg.MSG_ACTUATOR1_HS_STATE_ID):
        # elif(frame.port_id==limomsg.LimoMsg.MSG_ACTUATOR2_HS_STATE_ID):
        # elif(frame.port_id==limomsg.LimoMsg.MSG_ACTUATOR3_HS_STATE_ID):
        # elif(frame.port_id==limomsg.LimoMsg.MSG_ACTUATOR4_HS_STATE_ID):
        # elif(frame.port_id==limomsg.LimoMsg.MSG_ACTUATOR1_LS_STATE_ID):
        # elif(frame.port_id==limomsg.LimoMsg.MSG_ACTUATOR2_LS_STATE_ID):
        # elif(frame.port_id==limomsg.LimoMsg.MSG_ACTUATOR3_LS_STATE_ID):
        # elif(frame.port_id==limomsg.LimoMsg.MSG_ACTUATOR3_LS_STATE_ID):

    def EnableCommandMode(self):
        enable_frame = LimoFrame()
        enable_frame.port_id = limomsg.LimoMsg.MSG_CTRL_MODE_CONFIG_ID
        enable_frame.data[0] = 0x01
        enable_frame.data[1] = 0
        enable_frame.data[2] = 0
        enable_frame.data[3] = 0
        enable_frame.data[4] = 0
        enable_frame.data[5] = 0
        enable_frame.data[6] = 0
        enable_frame.data[7] = 0
        self.LimoSerialWrite(enable_frame)

    def SetMotionCommand(self,
                         linear_vel: float = 0.0,
                         angular_vel: float = 0.0,
                         lateral_velocity: float = 0.0,
                         steering_angle: float = 0.0):
        command_frame = LimoFrame()
        command_frame.port_id = limomsg.LimoMsg.MSG_MOTION_COMMAND_ID
        linear_cmd = linear_vel * 1000
        angular_cmd = angular_vel * 1000
        lateral_cmd = lateral_velocity * 1000
        steering_cmd = steering_angle * 1000
        command_frame.data[0] = int(linear_cmd) >> 8&0xff
        command_frame.data[1] = (int(linear_cmd) & 0x00ff)
        command_frame.data[2] = int(angular_cmd) >> 8&0xff
        command_frame.data[3] = (int(angular_cmd) & 0x00ff)
        command_frame.data[4] = int(lateral_cmd) >> 8&0xff
        command_frame.data[5] = (int(lateral_cmd) & 0x00ff)
        command_frame.data[6] = int(steering_cmd) >> 8&0xff
        command_frame.data[7] = (int(steering_cmd) & 0x00ff)
        self.LimoSerialWrite(command_frame)

    def ProcessErrorCode(self, error_code):
        if (error_code & 0x0001):
            print("LIMO: Low battery!")
        if (error_code & 0x0002):
            print("LIMO: Low battery!")
        if (error_code & 0x0004):
            print("LIMO: Remote control lost connect!")
        if (error_code & 0x0008):
            print("LIMO: Motor driver 1 error!")
        if (error_code & 0x0010):
            print("LIMO: Motor driver 2 error!")
        if (error_code & 0x0020):
            print("LIMO: Motor driver 3 error!")
        if (error_code & 0x0040):
            print("LIMO: Motor driver 4 error!")
        if (error_code & 0x0100):
            print("LIMO: Drive status error!")


class LimoFrame:
    def __init__(self,
                 stamp: float = 0.0,
                 port_id: ctypes.c_uint16 = 0,
                 count: ctypes.c_uint8 = 0,
                 data: Optional[bytearray] = None,
                 ):
        self.port_id = port_id
        self.stamp = stamp
        self.count = count
        #self.data = data
        if data is None:
            self.data = [0]*8
            #self.data = bytearray()
        elif isinstance(data, bytearray):
            self.data = data
        else:
            try:
                self.data = bytearray(data)
                #self.data = bytearray(data)
            except TypeError as error:
                err = f"Couldn't create message from {data} ({type(data)})"
                raise TypeError(err) from error


class LimoIMU:
    def __init__(self,
                 accel_x: float = 0.0,
                 accel_y: float = 0.0,
                 accel_z: float = 0.0,
                 gyro_x: float = 0.0,
                 gyro_y: float = 0.0,
                 gyro_z: float = 0.0,
                 yaw: float = 0.0,
                 pitch: float = 0.0,
                 roll: float = 0.0,

                 ):
        self.accel_x = accel_x
        self.accel_y = accel_y
        self.accel_z = accel_z
        self.gyro_x = gyro_x
        self.gyro_y = gyro_y
        self.gyro_z = gyro_z
        self.yaw = yaw
        self.pitch = pitch
        self.roll = roll
        #self.data = data


class LIMO:
    '''
    EnableCommand()
    SetMotionCommand()
    GetLinearVelocity()
    GetAngularVelocity()
    GetControlMode()
    GetBatteryVoltage()
    GetErrorCode()
    GetRightWheelOdem()
    GetLeftWheelOdem()
    GetIMUAccelData()
    GetIMUGyroData()
    GetIMUYawData()
    GetIMUPichData()
    GetIMURollData()
    '''
    def __init__(self, *device_args, **device_kwargs):
        serial_device_init_fn = LimoSerial.__init__
        args_names = serial_device_init_fn.__code__.co_varnames[:
                                                                serial_device_init_fn
                                                                .__code__.
                                                                co_argcount]
        args_dict = dict(zip(args_names, device_args))
        args_dict.update(device_kwargs)

        self.device = LimoSerial(**args_dict)
        self.wheelbase=0.2
        self.track= 0.172
        self.left_angle_scale = 2.47
        self.right_angle_scale = 1.64
        self.max_inner_angle = 0.48869
        self.max_lateral_velocity=1.0
    # def GetOdomMetry(self):
    #     wz=0.0
    #     vx=0.0
    #     vy=0.0
    #     if(limomsg.GetMotionMode()==0x00):
    #         vx=limomsg.GetLinearVelocity()
    #         vy=0.0
    #         wz=limomsg.GetAngularVelocity()
    #         return (vx,vy,wz)
    #     elif(limomsg.GetMotionMode()==0x01):            
    #         linear_velocity=limomsg.GetLinearVelocity()
    #         inner_angle = limomsg.GetSteeringAngle()
    #         #r = self.wheelbase/ math.tan(math.fabs(inner_angle)) + self.track / 2.0
    #         central_angle  = self.ConvertInnerAngleToCentral(inner_angle)
    #         if (central_angle > 0):
    #             try:
    #                 wz = linear_velocity / (self.wheelbase/ math.tan(math.fabs(inner_angle)) + self.track / 2.0)
    #             except ZeroDivisionError:
    #                 wz = linear_velocity/(self.track / 2.0)
    #         else :
    #             try:
    #                 wz = -linear_velocity / (self.wheelbase/ math.tan(math.fabs(inner_angle)) + self.track / 2.0)
    #             except ZeroDivisionError:
    #                 wz = -linear_velocity /(self.track / 2.0)  
    #         vx = linear_velocity * math.cos(central_angle)
    #         if (linear_velocity >= 0.0) :
    #             vy = linear_velocity * math.sin(central_angle)
            
    #         else :
    #             vy = linear_velocity * math.sin(-central_angle)
            
    #         return (vx,vy,wz)
        # elif(limomsg.GetMotionMode() ==0x02):
        #     vx = limomsg.GetLinearVelocity()
        #     vy = limomsg.GetLateralVelocity
        #     wz = limomsg.GetAngularVelocity()
        #     return (vx,vy,wz)
        # else:return (vx,vy,wz)
    # def SetMotionCommand(self,
                         
    #                      linear_x: float = 0.0,
    #                      linear_y: float = 0.0,
    #                      angular_z: float = 0.0):                
    #     '''
    #     fout diff  input linear_x and angular_z  
    #     ackermann  input linear_x and angular_z
    #     mcnamu     input linear_x linear_y angular_z
    #     '''
    #     if(limomsg.GetMotionMode()==0x00):
    #         self.device.SetMotionCommand(
    #         linear_x, angular_z, 0, 0)
    #     elif(limomsg.GetMotionMode()==0x01):
    #         try:
    #        # r=ctypes.c_double(linear_x/angular_z)
    #             central_angle = math.atan(self.wheelbase*angular_z/linear_x)
    #         except ZeroDivisionError:
    #             central_angle=0
    #         inner_angle = self.ConvertCentralAngleToInner(central_angle)
    #         if (inner_angle > self.max_inner_angle):
    #             inner_angle = self.max_inner_angle
            
    #         if (inner_angle < -self.max_inner_angle):
    #             inner_angle = -self.max_inner_angle
    #         if (inner_angle > 0) :
    #             steering_angle = inner_angle / self.left_angle_scale
    #         else :
    #             steering_angle = inner_angle / self.right_angle_scale
    #         self.device.SetMotionCommand(
    #         linear_x, 0, 0, steering_angle)
    #         # self.SetMotionCommand(linear_x, 0, 0, steering_angle)
    #     elif(limomsg.GetMotionMode() ==0x02):
    #         self.device.SetMotionCommand(
    #         linear_x, angular_z, linear_y,0 )
    #     else:print("motion mode not supported in receive cmd_vel")
            
    #     # self.device.SetMotionCommand(
    #     #     linear_vel, angular_vel, lateral_velocity, steering_angle)
    # def ConvertInnerAngleToCentral(self,inner_angle):
    #     try:

    #         r = self.wheelbase / math.tan(math.fabs(inner_angle)) + self.track / 2
    #     except ZeroDivisionError:
    #             r=self.track / 2
    #     central_angle = math.atan(self.wheelbase / r)

    #     if (inner_angle < 0): 
    #         central_angle = -central_angle
        

    #     return central_angle

    # def ConvertCentralAngleToInner(self,central_angle):
    #     inner_angle = math.atan(2 * self.wheelbase* math.sin(math.fabs(central_angle)) /
    #                                (2 * self.wheelbase * math.cos(math.fabs(central_angle)) -
    #                                 self.track * math.sin(math.fabs(central_angle))))

    #     if (central_angle < 0):
    #         inner_angle = -inner_angle
    #     return inner_angle

    def SetMotionCommand(self,
                         linear_vel: float = 0.0,
                         angular_vel: float = 0.0,
                         lateral_velocity: float = 0.0,
                         steering_angle: float = 0.0):
        if (steering_angle > self.max_inner_angle):
                steering_angle = self.max_inner_angle
            
        if (steering_angle < -self.max_inner_angle):
            steering_angle = -self.max_inner_angle

        if (angular_vel > self.left_angle_scale):
            angular_vel = self.left_angle_scale
            
        if (angular_vel < -self.left_angle_scale):
            angular_vel = -self.left_angle_scale 

        if (lateral_velocity > self.max_lateral_velocity):
            lateral_velocity = self.max_lateral_velocity
            
        if (lateral_velocity < -self.max_lateral_velocity):
            lateral_velocity = -self.max_lateral_velocity 

        self.device.SetMotionCommand(linear_vel,angular_vel,lateral_velocity,steering_angle)    


    def EnableCommand(self):
        '''
        Enable command and control mode
        '''
        self.device.EnableCommandMode()

    def GetLinearVelocity(self):
        '''
        Get the linear velocity from limo
        '''
        return limomsg.GetLinearVelocity()

    def GetAngularVelocity(self):
        '''
        Get the angular velocity from limo
        '''
        return limomsg.GetAngularVelocity()

    def GetSteeringAngle(self):
            '''
            Get the steering angle from limo
            '''
            return limomsg.GetSteeringAngle()

    def GetLateralVelocity(self):
            '''
            Get the lateral velocity from limo
            '''
            return limomsg.GetLateralVelocity()

    def GetControlMode(self):
        '''
        Get the control mode from limo
        '''
        return limomsg.GetControlMode()

    def GetBatteryVoltage(self):
        '''
        Get the battery voltage from limo
        '''
        return limomsg.GetBatteryVoltage()

    def GetErrorCode(self):
        return limomsg.GetErrorCode()

    def GetRightWheelOdom(self):
        return limomsg.GetRightWheelOdom()

    def GetLeftWheelOdeom(self):
        return limomsg.GetLeftWheelOdom()

    def GetIMUAccelData(self):
        return limomsg.GetIMUAccelX(), limomsg.GetIMUAccelY(), limomsg.GetIMUAccelZ()

    def GetIMUGyroData(self):
        return limomsg.GetIMUGyroX(), limomsg.GetIMUGyroY(), limomsg.GetIMUGyroZ()

    def GetIMUYawData(self):
        return limomsg.GetIMUYaw()

    def GetIMUPichData(self):
        return limomsg.GetIMUPitch()

    def GetIMURollData(self):
        return limomsg.GetIMURoll()

