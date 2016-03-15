# imuPIN - displacement_calibrated.py
# Stuart McDaniel, 2016

import graphing
import madgwick
import sensor_calibration
import sensor_read

import datetime
import os
import scipy.constants

# CONSTANTS.
# Number of sensor samples to read for calibration.
CALIBRATION_SAMPLES = 2000
# Number of sensor samples to read for analysis.
ANALYSIS_SAMPLES = 2000

# Starting orientation quaternion.
q = (1, 0, 0, 0)

# Open serial port.
ser = sensor_read.open_port()

# Calibrate sensor.
q = sensor_calibration.calibrate_by_time(ser, q, CALIBRATION_SAMPLES, True, True)

# Sensor samples measurements.
raw_acceleration = [(float(0), float(0), float(0))]
angular_velocity = [(float(0), float(0), float(0))]
gravity = [(float(0), float(0), float(0))]
acceleration = [(float(0), float(0), float(0))]
velocity_change = [(float(0), float(0), float(0))]
velocity = [(float(0), float(0), float(0))]
displacement_change = [(float(0), float(0), float(0))]
displacement = [(float(0), float(0), float(0))]

# Analysis.
for i in range(0, ANALYSIS_SAMPLES):
	# Get acceleration and angular velocity values from sensor packet.
	sensor_values = sensor_read.get_sensor_values(ser, "metres", "radians")

	# If values valid.
	if len(sensor_values) == 6:
		ax, ay, az, gx, gy, gz = sensor_values

		# Append sensor values to raw acceleration and angular velocity lists.
		raw_acceleration.append((ax, ay, az))
		angular_velocity.append((gx, gy, gz))

		# Calculate gravity on sample using Madgwick algorithm.
		q = madgwick.orientation_filter(q, angular_velocity[-1], raw_acceleration[-1])
		q0, q1, q2, q3 = q
		gravity.append((2 * (q1 * q3 - q0 * q2) * scipy.constants.g, 2 * (q0 * q1 + q2 * q3) * scipy.constants.g,
				(q0 * q0 - q1 * q1 - q2 * q2 + q3 * q3) * scipy.constants.g))

		# Remove gravity from raw acceleration.
		acceleration.append((raw_acceleration[-1][0] - gravity[-1][0],
				raw_acceleration[-1][1] - gravity[-1][1],
				raw_acceleration[-1][2] - gravity[-1][2]))

		# Get change in velocity during sample. Change in v = a * t.
		velocity_change.append((acceleration[-1][0] * (1 / madgwick.SAMPLE_FREQ),
				acceleration[-1][1] * (1 / madgwick.SAMPLE_FREQ),
				acceleration[-1][2] * (1 / madgwick.SAMPLE_FREQ)))

		# Calculate change in velocity's effect on overall velocity.
		velocity.append((velocity_change[-1][0] + velocity[-1][0], velocity_change[-1][1] + velocity[-1][1],
				velocity_change[-1][2] + velocity[-1][2]))

		# Get change in displacement during sample. Change in d = v * t.
		displacement_change.append((velocity[-1][0] * 0.01, velocity[-1][1] * 0.01, velocity[-1][2] * 0.01))

		# Calculate change in displacement's effect on overall displacement.
		displacement.append((displacement_change[-1][0] + displacement[-1][0],
				displacement_change[-1][1] + displacement[-1][1],
				displacement_change[-1][2] + displacement[-1][2]))

# Close serial port.
sensor_read.close_port(ser)

# Name of folder to save data in.
folder_name = str(datetime.datetime.now().strftime("%Y-%m-%d %H%M"))
os.makedirs(folder_name)

# Write column headers to file.
with open(folder_name + "/sensor_data.txt", "w") as data_file:
	data_file.write("Raw Acceleration (m/s^2) // Angular Velocity (rad/s) // Gravity (m/s^2) // Acceleration (m/s2) // "
			"Velocity (m/s) // Displacement (m)\n\n")

# Write sensor sample measurements to file.
with open(folder_name + "/sensor_data.txt", "a") as data_file:
	for i in range(0, len(raw_acceleration)):
		data_file.write("{:9.6f}".format(raw_acceleration[i + len(raw_acceleration) - len(displacement)][0]) + ", " +
				"{:9.6f}".format(raw_acceleration[i + len(raw_acceleration) - len(displacement)][1]) + ", " +
				"{:9.6f}".format(raw_acceleration[i + len(raw_acceleration) - len(displacement)][2]) + " // " +
				"{:9.6f}".format(angular_velocity[i + len(raw_acceleration) - len(displacement)][0]) + ", " +
				"{:9.6f}".format(angular_velocity[i + len(raw_acceleration) - len(displacement)][1]) + ", " +
				"{:9.6f}".format(angular_velocity[i + len(raw_acceleration) - len(displacement)][2]) + " // " +
				"{:9.6f}".format(gravity[i + len(raw_acceleration) - len(displacement)][0]) + ", " +
				"{:9.6f}".format(gravity[i + len(raw_acceleration) - len(displacement)][1]) + ", " +
				"{:9.6f}".format(gravity[i + len(raw_acceleration) - len(displacement)][2]) + " // " +
				"{:9.6f}".format(acceleration[i][0]) + ", " +
				"{:9.6f}".format(acceleration[i][1]) + ", " +
				"{:9.6f}".format(acceleration[i][2]) + " // " +
				"{:9.6f}".format(velocity[i][0]) + ", " +
				"{:9.6f}".format(velocity[i][1]) + ", " +
				"{:9.6f}".format(velocity[i][2]) + " // " +
				"{:9.6f}".format(displacement[i][0]) + ", " +
				"{:9.6f}".format(displacement[i][1]) + ", " +
				"{:9.6f}".format(displacement[i][2]) + "\n\n")

# Plot displacement graph.
graphing.plot_displacement_graph(displacement, 2, folder_name + "/graph.mp4")
