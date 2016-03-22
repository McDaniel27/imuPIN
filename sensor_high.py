# imuPIN - sensor_high.py
# Stuart McDaniel, 2016

import madgwick
import sensor_low
import utils

import numpy
import os
import peakutils
import scipy.constants


# Calibrate sensor by calculating orientation quaternion after number of samples.
def calibrate_sensor_time(ser, q, samples, metres, radians):
	# For each sample.
	for i in range(samples):
		# Get acceleration and angular velocity values from sensor packet.
		sensor_values = sensor_low.get_sensor_values(ser, metres, radians)

		# If values valid.
		if len(sensor_values) == 6:
			ax, ay, az, gx, gy, gz = sensor_values

			# Calculate orientation quaternion of sensor sample using previous quaternion.
			q = madgwick.orientation_filter(q, (ax, ay, az), (gx, gy, gz))

	# Announce sensor calibrated.
	os.system("say 'calibrated'")

	return q


# Calibrate sensor by reading samples until gravity relatively constant.
def calibrate_sensor_compare(ser, q, metres, radians):
	# Sensor samples measurements.
	raw_acceleration = []
	angular_velocity = []
	gravity = []

	while True:
		# Get acceleration and angular velocity values from sensor packet.
		sensor_values = sensor_low.get_sensor_values(ser, metres, radians)

		# If values valid.
		if len(sensor_values) == 6:
			ax, ay, az, gx, gy, gz = sensor_values

			# Append sensor values to raw acceleration and angular velocity lists.
			raw_acceleration.append((ax, ay, az))
			angular_velocity.append((gx, gy, gz))

			# Calculate orientation quaternion of sensor sample using previous quaternion.
			q = madgwick.orientation_filter(q, (gx, gy, gz), (ax, ay, az))

			# Calculate gravity on sample using orientation quaternion.
			q0, q1, q2, q3 = q
			if metres:
				gravity.append((2 * (q1 * q3 - q0 * q2) * scipy.constants.g,
						2 * (q0 * q1 + q2 * q3) * scipy.constants.g,
						(q0 * q0 - q1 * q1 - q2 * q2 + q3 * q3) * scipy.constants.g))
			else:
				gravity.append((2 * (q1 * q3 - q0 * q2),
						2 * (q0 * q1 + q2 * q3),
						q0 * q0 - q1 * q1 - q2 * q2 + q3 * q3))

		if metres:
			# If gravity relatively constant.
			if len(gravity) >= 10 and utils.within_range(gravity[-10:], 0.04):
				break
		else:
			# If gravity relatively constant.
			if len(gravity) >= 10 and utils.within_range(gravity[-10:], 0.04 / scipy.constants.g):
				break

	# Announce sensor calibrated.
	os.system("say 'calibrated'")

	return q


# Get acceleration samples.
def get_acceleration(ser, q, samples, metres, radians):
	# Sensor samples measurements.
	raw_acceleration = []
	angular_velocity = []
	gravity = []
	acceleration = []

	# For each sample.
	for i in range(samples):
		# Get acceleration and angular velocity values from sensor packet.
		sensor_values = sensor_low.get_sensor_values(ser, metres, radians)

		# If values valid.
		if len(sensor_values) == 6:
			ax, ay, az, gx, gy, gz = sensor_values

			# Append sensor values to raw acceleration and angular velocity lists.
			raw_acceleration.append((ax, ay, az))
			angular_velocity.append((gx, gy, gz))

			# Calculate orientation quaternion of sensor sample using previous quaternion.
			q = madgwick.orientation_filter(q, (gx, gy, gz), (ax, ay, az))

			# Calculate gravity on sample using orientation quaternion.
			q0, q1, q2, q3 = q
			if metres:
				gravity.append((2 * (q1 * q3 - q0 * q2) * scipy.constants.g,
						2 * (q0 * q1 + q2 * q3) * scipy.constants.g,
						(q0 * q0 - q1 * q1 - q2 * q2 + q3 * q3) * scipy.constants.g))
			else:
				gravity.append((2 * (q1 * q3 - q0 * q2),
						2 * (q0 * q1 + q2 * q3),
						q0 * q0 - q1 * q1 - q2 * q2 + q3 * q3))

			# Remove gravity from raw acceleration.
			acceleration.append((raw_acceleration[-1][0] - gravity[-1][0],
					raw_acceleration[-1][1] - gravity[-1][1],
					raw_acceleration[-1][2] - gravity[-1][2]))

	return q, raw_acceleration, angular_velocity, gravity, acceleration


# Convert acceleration samples to get displacement samples.
def get_displacement(acceleration):
	# Sensor samples measurements.
	velocity_change = []
	velocity = [(float(0), float(0), float(0))]
	displacement_change = []
	displacement = [(float(0), float(0), float(0))]

	# For each acceleration sample.
	for i in range(len(acceleration)):
		# Get change in velocity during sample. Change in v = a * t.
		velocity_change.append((acceleration[-1][0] * (1 / madgwick.SAMPLE_FREQ),
				acceleration[-1][1] * (1 / madgwick.SAMPLE_FREQ),
				acceleration[-1][2] * (1 / madgwick.SAMPLE_FREQ)))

		# Calculate change in velocity's effect on overall velocity.
		velocity.append((velocity_change[-1][0] + velocity[-1][0],
				velocity_change[-1][1] + velocity[-1][1],
				velocity_change[-1][2] + velocity[-1][2]))

		# Get change in displacement during sample. Change in d = v * t.
		displacement_change.append((velocity[-1][0] * (1 / madgwick.SAMPLE_FREQ),
				velocity[-1][1] * (1 / madgwick.SAMPLE_FREQ),
				velocity[-1][2] * (1 / madgwick.SAMPLE_FREQ)))

		# Calculate change in displacement's effect on overall displacement.
		displacement.append((displacement_change[-1][0] + displacement[-1][0],
				displacement_change[-1][1] + displacement[-1][1],
				displacement_change[-1][2] + displacement[-1][2]))

	# Remove dummy values.
	velocity.pop(0)
	displacement.pop(0)

	return velocity_change, velocity, displacement_change, displacement


# Quantise acceleration samples (compression).
def quantisation_compress(acceleration, window_size, window_slide):
	# Average acceleration samples using sliding window.
	compressed = []
	for i in range(len(acceleration)):
		if i % window_slide == 0:
			compressed.append((sum([x[0] for x in acceleration[i:i + window_size]]) / window_size,
					sum([x[1] for x in acceleration[i:i + window_size]]) / window_size,
					sum([x[2] for x in acceleration[i:i + window_size]]) / window_size))

	return compressed


# Quantise acceleration samples (discretion).
def quantisation_discrete(acceleration):
	# Convert each acceleration sample into one of 33 levels (-16 to 16).
	discrete = []
	for i in range(len(acceleration)):
		discrete.append([0, 0, 0])
		for j in range(3):
			if acceleration[i][j] > 2:
				discrete[-1][j] = 16
			elif acceleration[i][j] > 1:
				discrete[-1][j] = round((acceleration[i][j] - 1) * 5) + 10
			elif acceleration[i][j] > 0:
				discrete[-1][j] = round(acceleration[i][j] * 10)
			elif acceleration[i][j] == 0:
				discrete[-1][j] = 0
			elif acceleration[i][j] > -1:
				discrete[-1][j] = round(acceleration[i][j] * 10)
			elif acceleration[i][j] > -2:
				discrete[-1][j] = round((acceleration[i][j] + 1) * 5) - 10
			else:
				discrete[-1][j] = -16

	return discrete


# Get axis peaks in acceleration samples.
def find_peaks(acceleration, peaks_axis):
	# Convert list of (x, y, z) tuples into array of arrays of x, y, and z values.
	acceleration_array = utils.convert_tuples(acceleration)

	# Get peaks.
	peaks = peakutils.peak.indexes(numpy.array(acceleration_array[peaks_axis]), thres=0.25, min_dist=10)

	return peaks


# Segment sections of acceleration data containing PIN entry.
def segment(acceleration, peaks):
	segments = []

	# If enough peaks to contain PIN entry.
	if len(peaks) >= 4:
		# For each series of four peaks.
		for i in range(len(peaks) - 3):
			# Create and zero possible PIN entry segment.
			# [2, 4, 6, 8] becomes [0, 2, 4, 6].
			possible_segment = list(peaks[i:i + 4])
			for j in range(3, -1, -1):
				possible_segment[j] -= possible_segment[0]

			segment_length = possible_segment[3] - possible_segment[0]
			# If second key press is ~1/3 into four key presses.
			if 0.19 <= (possible_segment[1] / segment_length) <= 0.47:
				# If third key press is ~2/3 into four key presses.
				if 0.52 <= (possible_segment[2] / segment_length) <= 0.80:
					segments.append(list(acceleration[peaks[i] - 2:peaks[i + 3] + 3]))

	return segments


# Extract PIN transitions from PIN entry segment.
def extract(segment):
	# Get peaks in segment.
	peaks = find_peaks(segment, 2)

	# Extract acceleration data between peaks.
	features = []
	for i in range(len(peaks) - 1):
		features.append(list(segment[peaks[i]:peaks[i + 1] + 1]))

	return features
