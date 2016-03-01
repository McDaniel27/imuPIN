# imuPIN - sensor.py
# Stuart McDaniel, 2016

import ctypes
import math
import serial
import scipy.constants

# Serial port name.
port = '/dev/cu.WAX9-DCDD-COM1'

# Accelerometer normalisation value.
acc_norm = 4096.0 / scipy.constants.g
# Gyrometer normalisation value.
gyro_norm = math.radians(0.07)


# Open named serial port for reading.
def open_port():
	# Open serial port.
	ser = serial.Serial(
		port=port,
		baudrate=115200,
		bytesize=serial.EIGHTBITS,
		parity=serial.PARITY_NONE,
		stopbits=serial.STOPBITS_ONE,
		timeout=5
	)

	# Write start stream command.
	ser.write('stream=1\r\n'.encode('utf-8'))

	return ser


# Get acceleration and angular velocity values from sensor packet.
def get_sensor_values(ser):
	# Read bytes until read SLIP END byte to start packet.
	# Python does not have do-while loop.
	while True:
		data = ser.read(size=1)
		if data[0] == 192:
			break

	# Read and append bytes until read SLIP END byte to end packet.
	# Python does not have do-while loop.
	while True:
		data += ser.read(size=1)
		if data[-1] == 192:
			break

	# If sensor packet valid.
	if len(data) in (28, 36):
		# Print packet length.
		# print("Length:", len(data))

		# Print packet bytes.
		print("Data: ", end="")
		for i in range(0, len(data)):
			print(str(data[i]) + " ", end="")
		print()

		# Convert and normalise accelerometer bytes to get acceleration on each axis in m/s^2.
		# Uses C types to achieve exact 8-bit/16-bit and signed/unsigned precision.
		ax = ctypes.c_int16(ctypes.c_ushort(data[10] << 8).value + ctypes.c_ushort(data[9]).value).value / acc_norm
		ay = ctypes.c_int16(ctypes.c_ushort(data[12] << 8).value + ctypes.c_ushort(data[11]).value).value / acc_norm
		az = ctypes.c_int16(ctypes.c_ushort(data[14] << 8).value + ctypes.c_ushort(data[13]).value).value / acc_norm

		# Convert and normalise gyrometer bytes to get angular velocity on each axis in rad/s.
		# Uses C types to achieve exact 8-bit/16-bit and signed/unsigned precision.
		gx = ctypes.c_int16(ctypes.c_ushort(data[16] << 8).value + ctypes.c_ushort(data[15]).value).value * gyro_norm
		gy = ctypes.c_int16(ctypes.c_ushort(data[18] << 8).value + ctypes.c_ushort(data[17]).value).value * gyro_norm
		gz = ctypes.c_int16(ctypes.c_ushort(data[20] << 8).value + ctypes.c_ushort(data[19]).value).value * gyro_norm

		# Print acceleration and angular velocity values.
		# print("Acceleration:", ax, ay, az)
		# print("Angular Velocity:", gx, gy, gz)
		# print()

		return [ax, ay, az, gx, gy, gz]
	else:
		return []


# Close named serial port.
def close_port(ser):
	ser.close()
