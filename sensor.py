# imuPIN - sensor.py
# Stuart McDaniel, 2016

import utils

import ctypes
import math
import scipy.constants
import serial

# CONSTANTS.
# Start/end of packet indicator byte.
SLIP_END = 192
# Second byte.
SECOND = 57
# Escape byte.
SLIP_ESC = 219
# Escaped substitution for SLIP_END byte.
SLIP_ESC_END = 220
# Escaped substitution for SLIP_ESC byte.
SLIP_ESC_ESC = 221
# Valid packet lengths.
PACKET_LENGTHS = [28, 36]


# Open named serial port for reading.
def open_serial_port():
	# Open serial port.
	ser = serial.Serial(
		port=utils.SERIAL_PORT,
		baudrate=115200,
		bytesize=serial.EIGHTBITS,
		parity=serial.PARITY_NONE,
		stopbits=serial.STOPBITS_ONE,
		timeout=5
	)

	# Write start stream command.
	ser.write("stream=1\r\n".encode("utf-8"))

	return ser


# Get acceleration and angular velocity values from packet.
def get_sensor_values(ser, metres, radians):
	# Accelerometer normalisation value for m/s^2.
	if metres:
		acc_norm = 4096.0 / scipy.constants.g
	# Accelerometer normalisation value for g.
	else:
		acc_norm = 4096.0

	# Gyrometer normalisation value for rad/s.
	if radians:
		gyro_norm = math.radians(0.07)
	# Gyrometer normalisation value for deg/s.
	else:
		gyro_norm = 0.07

	packet = []

	# Read first two bytes until found SLIP_END and SECOND bytes to indicate start of packet.
	chars = [ser.read(size=1)[0]]
	while True:
		chars.append(ser.read(size=1)[0])
		if chars[0] == SLIP_END and chars[1] == SECOND:
			packet.append(chars[0])
			packet.append(chars[1])
			break
		else:
			chars = [chars[1]]

	# Read and append bytes until found SLIP_END byte to indicate end of packet.
	escaped = False
	while True:
		char = ser.read(size=1)[0]
		# End of packet.
		if char == SLIP_END:
			packet.append(char)
			break
		# SLIP_ESC_END or SLIP_ESC_ESC will follow.
		elif char == SLIP_ESC:
			escaped = True
		# SLIP_ESC SLIP_ESC_END represents SLIP_END in data.
		elif char == SLIP_ESC_END:
			if escaped:
				packet.append(SLIP_END)
				escaped = False
			else:
				packet.append(char)
		# SLIP_ESC SLIP_ESC_ESC represents SLIP_ESC in data.
		elif char == SLIP_ESC_ESC:
			if escaped:
				packet.append(SLIP_ESC)
				escaped = False
			else:
				packet.append(char)
		# Any other byte.
		else:
			packet.append(char)

	# If packet valid.
	if len(packet) in PACKET_LENGTHS:
		# Print packet length.
		# print("Length:", len(data))

		# Print packet bytes.
		# print("Data: ", end="")
		# for byte in packet:
			# print("{:3d}".format(byte) + " ", end="")
		# print()

		# Convert and normalise accelerometer bytes to get acceleration on each axis.
		# Uses C types to achieve exact 8-bit/16-bit and signed/unsigned precision.
		ax = ctypes.c_int16(ctypes.c_ushort(packet[10] << 8).value + ctypes.c_ushort(packet[9]).value).value / acc_norm
		ay = ctypes.c_int16(ctypes.c_ushort(packet[12] << 8).value + ctypes.c_ushort(packet[11]).value).value / acc_norm
		az = ctypes.c_int16(ctypes.c_ushort(packet[14] << 8).value + ctypes.c_ushort(packet[13]).value).value / acc_norm

		# Convert and normalise gyrometer bytes to get angular velocity on each axis.
		# Uses C types to achieve exact 8-bit/16-bit and signed/unsigned precision.
		gx = ctypes.c_int16(ctypes.c_ushort(packet[16] << 8).value + ctypes.c_ushort(packet[15]).value).value * gyro_norm
		gy = ctypes.c_int16(ctypes.c_ushort(packet[18] << 8).value + ctypes.c_ushort(packet[17]).value).value * gyro_norm
		gz = ctypes.c_int16(ctypes.c_ushort(packet[20] << 8).value + ctypes.c_ushort(packet[19]).value).value * gyro_norm

		# Print acceleration and angular velocity values.
		# print("Acceleration: " + str(ax) + ", " + str(ay) + ", " + str(az))
		# print("Angular Velocity: " + str(gx) + ", " + str(gy) + ", " + str(gz) + "\n")

		return ax, ay, az, gx, gy, gz
	else:
		return ()


# Close named serial port.
def close_serial_port(ser):
	ser.close()
