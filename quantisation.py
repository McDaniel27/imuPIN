# imuPIN - quantisation.py
# Stuart McDaniel, 2016

import graphing
import madgwick
import sensor_calibration
import sensor_read

import datetime
import os

# CONSTANTS.
# Number of sensor samples to read for calibration.
CALIBRATION_SAMPLES = 2000
# Number of sensor samples to read for analysis.
ANALYSIS_SAMPLES = 2000
# Number of packets in sliding window.
WINDOW_SIZE = 5
# Number of packets sliding window slides.
WINDOW_SLIDE = 3

# Starting orientation quaternion.
q = (1, 0, 0, 0)

# Open serial port.
ser = sensor_read.open_port()

# Calibrate sensor.
q = sensor_calibration.calibrate_by_time(ser, q, CALIBRATION_SAMPLES, True, True)

# Sensor samples measurements.
raw_acceleration = []
angular_velocity = []
gravity = []
acceleration = []

# Analysis.
for i in range(0, ANALYSIS_SAMPLES):
	# Get acceleration and angular velocity values from sensor packet.
	sensor_values = sensor_read.get_sensor_values(ser, False, True)

	# If values valid.
	if len(sensor_values) == 6:
		ax, ay, az, gx, gy, gz = sensor_values

		# Append sensor values to raw acceleration and angular velocity lists.
		raw_acceleration.append((ax, ay, az))
		angular_velocity.append((gx, gy, gz))

		# Calculate gravity on sample using Madgwick algorithm.
		q = madgwick.orientation_filter(q, angular_velocity[-1], raw_acceleration[-1])
		q0, q1, q2, q3 = q
		gravity.append((2 * (q1 * q3 - q0 * q2), 2 * (q0 * q1 + q2 * q3), (q0 * q0 - q1 * q1 - q2 * q2 + q3 * q3)))

		# Remove gravity from raw acceleration.
		acceleration.append((raw_acceleration[-1][0] - gravity[-1][0],
				raw_acceleration[-1][1] - gravity[-1][1],
				raw_acceleration[-1][2] - gravity[-1][2]))

compressed = []

# Quantisation via compression (sliding window).
for i in range(0, len(acceleration)):
	if i % WINDOW_SLIDE == 0:
		compressed.append((sum([x[0] for x in acceleration[i:i + WINDOW_SIZE]]) / WINDOW_SIZE,
				sum([x[1] for x in acceleration[i:i + WINDOW_SIZE]]) / WINDOW_SIZE,
				sum([x[2] for x in acceleration[i:i + WINDOW_SIZE]]) / WINDOW_SIZE))

discrete = []

# Quantisation via discretion (converted into one of 33 levels).
for i in range(0, len(compressed)):
	discrete.append([0, 0, 0])
	for j in range(0, 3):
		if compressed[i][j] > 2:
			discrete[-1][j] = 16
		elif compressed[i][j] > 1:
			discrete[-1][j] = round((compressed[i][j] - 1) * 5) + 10
		elif compressed[i][j] > 0:
			discrete[-1][j] = round(compressed[i][j] * 10)
		elif compressed[i][j] == 0:
			discrete[-1][j] = 0
		elif compressed[i][j] > -1:
			discrete[-1][j] = round(compressed[i][j] * 10)
		elif compressed[i][j] > -2:
			discrete[-1][j] = round((compressed[i][j] + 1) * 5) - 10
		else:
			discrete[-1][j] = -16

# Close serial port.
sensor_read.close_port(ser)

# Name of folder to save data in.
folder_name = str(datetime.datetime.now().strftime("%Y-%m-%d %H%M"))
os.makedirs(folder_name)

# Write column headers to file.
with open(folder_name + "/sensor_data.txt", 'w') as data_file:
	data_file.write("Raw Acceleration (g) // Angular Velocity (rad/s) // Gravity (g) // Acceleration (g) // "
			"Compressed Acceleration (g) // Discrete Acceleration\n\n")

# Write sensor samples measurements to file.
with open(folder_name + "/sensor_data.txt", "a") as data_file:
	for i in range(0, len(raw_acceleration) - 30):
		data_file.write("{:9.6f}".format(raw_acceleration[i][0]) + ", " +
				"{:9.6f}".format(raw_acceleration[i][1]) + ", " +
				"{:9.6f}".format(raw_acceleration[i][2]) + " // " +
				"{:9.6f}".format(angular_velocity[i][0]) + ", " +
				"{:9.6f}".format(angular_velocity[i][1]) + ", " +
				"{:9.6f}".format(angular_velocity[i][2]) + " // " +
				"{:9.6f}".format(gravity[i][0]) + ", " +
				"{:9.6f}".format(gravity[i][1]) + ", " +
				"{:9.6f}".format(gravity[i][2]) + " // " +
				"{:9.6f}".format(acceleration[i][0]) + ", " +
				"{:9.6f}".format(acceleration[i][1]) + ", " +
				"{:9.6f}".format(acceleration[i][2]))
		if i % WINDOW_SLIDE == 0:
			data_file.write(" // " +
					"{:9.6f}".format(compressed[i // WINDOW_SLIDE][0]) + ", " +
					"{:9.6f}".format(compressed[i // WINDOW_SLIDE][1]) + ", " +
					"{:9.6f}".format(compressed[i // WINDOW_SLIDE][2]) + " // " +
					"{:3d}".format(discrete[i // WINDOW_SLIDE][0]) + ", " +
					"{:3d}".format(discrete[i // WINDOW_SLIDE][1]) + ", " +
					"{:3d}".format(discrete[i // WINDOW_SLIDE][2]))
		data_file.write("\n\n")

graphing.plot_acceleration_graph(acceleration, 2, folder_name + "/raw_graph.png")
graphing.plot_acceleration_graph(compressed, 2, folder_name + "/compressed_graph.png")
graphing.plot_acceleration_graph(discrete, 16, folder_name + "/discrete_graph.png")
