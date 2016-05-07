# imuPIN - sensor_samples.py
# Stuart McDaniel, 2016

import madgwick
import sensor
import utils

import scipy.constants


# Calibrate sensor by calculating orientation quaternion after number of samples.
def calibrate_sensor_time(ser, q, samples, metres, radians):
	# For each sample.
	for i in range(samples):
		# Get acceleration and angular velocity values from packet.
		sensor_values = sensor.get_sensor_values(ser, metres, radians)

		# If values valid.
		if len(sensor_values) == 6:
			ax, ay, az, gx, gy, gz = sensor_values

			# Calculate orientation quaternion of sensor sample using previous quaternion.
			q = madgwick.orientation_filter(q, (ax, ay, az), (gx, gy, gz))

	return q


# Calibrate sensor by reading samples until gravity relatively constant.
def calibrate_sensor_compare(ser, q, metres, radians):
	raw_acceleration = [], [], []
	angular_velocity = [], [], []
	gravity = [], [], []

	while True:
		# Get acceleration and angular velocity values from packet.
		sensor_values = sensor.get_sensor_values(ser, metres, radians)

		# If values valid.
		if len(sensor_values) == 6:
			ax, ay, az, gx, gy, gz = sensor_values

			# Append sensor values to raw acceleration and angular velocity lists.
			raw_acceleration[0].append(ax)
			raw_acceleration[1].append(ay)
			raw_acceleration[2].append(az)
			angular_velocity[0].append(gx)
			angular_velocity[1].append(gy)
			angular_velocity[2].append(gz)

			# Calculate orientation quaternion of sensor sample using previous quaternion.
			q = madgwick.orientation_filter(q, (gx, gy, gz), (ax, ay, az))

			# Calculate gravity on sample using orientation quaternion.
			q0, q1, q2, q3 = q
			if metres:
				gravity[0].append(2 * (q1 * q3 - q0 * q2) * scipy.constants.g)
				gravity[1].append(2 * (q0 * q1 + q2 * q3) * scipy.constants.g)
				gravity[2].append((q0 * q0 - q1 * q1 - q2 * q2 + q3 * q3) * scipy.constants.g)
			else:
				gravity[0].append(2 * (q1 * q3 - q0 * q2))
				gravity[1].append(2 * (q0 * q1 + q2 * q3))
				gravity[2].append(q0 * q0 - q1 * q1 - q2 * q2 + q3 * q3)

		# Break if gravity relatively constant.
		if metres:
			if len(gravity[0]) >= 10 and utils.list_within_range((gravity[0][-10:], gravity[1][-10:], gravity[2][-10:]), 0.04):
				break
		else:
			if len(gravity[0]) >= 10 and utils.list_within_range((gravity[0][-10:], gravity[1][-10:], gravity[2][-10:]),
																 0.04 / scipy.constants.g):
				break

	return q


# Get acceleration samples.
def get_acceleration(ser, q, samples, metres, radians):
	raw_acceleration = [], [], []
	angular_velocity = [], [], []
	gravity = [], [], []
	acceleration = [], [], []

	# For each sample.
	for i in range(samples):
		# Get acceleration and angular velocity values from packet.
		sensor_values = sensor.get_sensor_values(ser, metres, radians)

		# If values valid.
		if len(sensor_values) == 6:
			ax, ay, az, gx, gy, gz = sensor_values

			# Append sensor values to raw acceleration and angular velocity lists.
			raw_acceleration[0].append(ax)
			raw_acceleration[1].append(ay)
			raw_acceleration[2].append(az)
			angular_velocity[0].append(gx)
			angular_velocity[1].append(gy)
			angular_velocity[2].append(gz)

			# Calculate orientation quaternion of sensor sample using previous quaternion.
			q = madgwick.orientation_filter(q, (gx, gy, gz), (ax, ay, az))

			# Calculate gravity on sample using orientation quaternion.
			q0, q1, q2, q3 = q
			if metres:
				gravity[0].append(2 * (q1 * q3 - q0 * q2) * scipy.constants.g)
				gravity[1].append(2 * (q0 * q1 + q2 * q3) * scipy.constants.g)
				gravity[2].append((q0 * q0 - q1 * q1 - q2 * q2 + q3 * q3) * scipy.constants.g)
			else:
				gravity[0].append(2 * (q1 * q3 - q0 * q2))
				gravity[1].append(2 * (q0 * q1 + q2 * q3))
				gravity[2].append(q0 * q0 - q1 * q1 - q2 * q2 + q3 * q3)

			# Remove gravity from raw acceleration.
			acceleration[0].append(raw_acceleration[0][-1] - gravity[0][-1])
			acceleration[1].append(raw_acceleration[1][-1] - gravity[1][-1])
			acceleration[2].append(raw_acceleration[2][-1] - gravity[2][-1])

	return q, raw_acceleration, angular_velocity, gravity, acceleration


# Double integrate acceleration samples to get displacement samples.
def get_displacement(acceleration):
	velocity_change = [], [], []
	velocity = [0.0], [0.0], [0.0]
	displacement_change = [], [], []
	displacement = [0.0], [0.0], [0.0]

	# For each acceleration sample.
	for i in range(len(acceleration[0])):
		# Get change in velocity during sample. Change in v = a * t.
		velocity_change[0].append(acceleration[0][-1] * (1 / utils.SAMPLE_FREQ))
		velocity_change[1].append(acceleration[1][-1] * (1 / utils.SAMPLE_FREQ))
		velocity_change[2].append(acceleration[2][-1] * (1 / utils.SAMPLE_FREQ))

		# Calculate change in velocity's effect on overall velocity.
		velocity[0].append(velocity_change[0][-1] + velocity[0][-1])
		velocity[1].append(velocity_change[1][-1] + velocity[1][-1])
		velocity[2].append(velocity_change[2][-1] + velocity[2][-1])

		# Get change in displacement during sample. Change in d = v * t.
		displacement_change[0].append(velocity[0][-1] * (1 / utils.SAMPLE_FREQ))
		displacement_change[1].append(velocity[1][-1] * (1 / utils.SAMPLE_FREQ))
		displacement_change[2].append(velocity[2][-1] * (1 / utils.SAMPLE_FREQ))

		# Calculate change in displacement's effect on overall displacement.
		displacement[0].append(displacement_change[0][-1] + displacement[0][-1])
		displacement[1].append(displacement_change[1][-1] + displacement[1][-1])
		displacement[2].append(displacement_change[2][-1] + displacement[2][-1])

	# Remove dummy values.
	velocity[0].pop(0)
	velocity[1].pop(0)
	velocity[2].pop(0)
	displacement[0].pop(0)
	displacement[1].pop(0)
	displacement[2].pop(0)

	return velocity_change, velocity, displacement_change, displacement


# Quantise acceleration samples (temporal compression).
def quantise_compress(acceleration):
	# Average acceleration samples using sliding window.
	compressed = [], [], []
	for i in range(len(acceleration[0])):
		if i % utils.WINDOW_SLIDE == 0:
			compressed[0].append(sum(acceleration[0][i:i + utils.WINDOW_SIZE]) / utils.WINDOW_SIZE)
			compressed[1].append(sum(acceleration[1][i:i + utils.WINDOW_SIZE]) / utils.WINDOW_SIZE)
			compressed[2].append(sum(acceleration[2][i:i + utils.WINDOW_SIZE]) / utils.WINDOW_SIZE)

	return compressed


# Quantise acceleration samples (non-linear conversion).
def quantise_discrete(acceleration):
	# Convert each acceleration sample into one of 33 levels (-16 to 16).
	discrete = [], [], []
	for i in range(3):
		for j in range(len(acceleration[i])):
			if acceleration[i][j] > 2:
				discrete[i].append(16)
			elif acceleration[i][j] > 1:
				discrete[i].append(round((acceleration[i][j] - 1) * 5) + 10)
			elif acceleration[i][j] > 0:
				discrete[i].append(round(acceleration[i][j] * 10))
			elif acceleration[i][j] == 0:
				discrete[i].append(0)
			elif acceleration[i][j] > -1:
				discrete[i].append(round(acceleration[i][j] * 10))
			elif acceleration[i][j] > -2:
				discrete[i].append(round((acceleration[i][j] + 1) * 5) - 10)
			else:
				discrete[i].append(-16)

	return discrete
