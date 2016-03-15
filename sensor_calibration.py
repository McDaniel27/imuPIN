# imuPIN - sensor_calibration.py
# Stuart McDaniel, 2016

import madgwick
import sensor_read

import os
import scipy.constants


# Calibrate sensor by calculating q on number of samples.
def calibrate_by_time(ser, q, samples, metres, radians):
	for i in range(0, samples):
		# Get acceleration and angular velocity values from sensor packet.
		sensor_values = sensor_read.get_sensor_values(ser, metres, radians)

		# If values valid.
		if len(sensor_values) == 6:
			ax, ay, az, gx, gy, gz = sensor_values

			# Calculate gravity quaternion of sample using Madgwick algorithm.
			q = madgwick.orientation_filter(q, (ax, ay, az), (gx, gy, gz))

	# Announce sensor calibrated.
	os.system("say 'calibrated'")

	return q


# Calibrate sensor by reading samples until gravity relatively constant.
def calibrate_by_compare(ser, q, metres, radians):
	raw_acceleration = []
	angular_velocity = []
	gravity = []

	while True:
		# Get acceleration and angular velocity values from sensor packet.
		sensor_values = sensor_read.get_sensor_values(ser, metres, radians)

		# If values valid.
		if len(sensor_values) == 6:
			ax, ay, az, gx, gy, gz = sensor_values

			# Append sensor values to raw acceleration and angular velocity lists.
			raw_acceleration.append((ax, ay, az))
			angular_velocity.append((gx, gy, gz))

			# Calculate gravity on sample using Madgwick algorithm.
			q = madgwick.orientation_filter(q, angular_velocity[-1], raw_acceleration[-1])
			q0, q1, q2, q3 = q
			if metres:
				gravity.append((2 * (q1 * q3 - q0 * q2) * scipy.constants.g, 2 * (q0 * q1 + q2 * q3) * scipy.constants.g,
						(q0 * q0 - q1 * q1 - q2 * q2 + q3 * q3) * scipy.constants.g))
			else:
				gravity.append((2 * (q1 * q3 - q0 * q2), 2 * (q0 * q1 + q2 * q3), (q0 * q0 - q1 * q1 - q2 * q2 + q3 * q3)))

		# If gravity relatively constant.
		if len(gravity) >= 10 and within_range(gravity[-10:], 0.05):
			break

	# Announce sensor calibrated.
	os.system("say 'calibrated'")

	return q


# Calculate if number of values in tuple are within certain range of each other.
def within_range(tuples, range_value):
	within = True
	for i in range(0, len(tuples) - 1):
		for j in range((i + 1), len(tuples)):
			if abs(tuples[i][0] - tuples[j][0]) > range_value or abs(tuples[i][1] - tuples[j][1]) > range_value or \
					abs(tuples[i][2] - tuples[j][2]) > range_value:
				within = False

	return within
