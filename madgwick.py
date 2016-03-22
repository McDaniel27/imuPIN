# imuPIN - madgwick.py
# Stuart McDaniel, 2016

# Python translation of Sebastian Madgwick's IMU sensor fusion orientation filter.
# http://www.x-io.co.uk/res/doc/madgwick_internal_report.pdf
# http://ieeexplore.ieee.org/xpls/abs_all.jsp?arnumber=5975346
# http://www.x-io.co.uk/res/sw/madgwick_algorithm_c.zip

# CONSTANTS.
# Algorithm beta gain.
BETA_GAIN = 0.1
# Sample frequency of sensor in Hz.
SAMPLE_FREQ = 100.0


# Calculate orientation quaternion of sensor sample using previous quaternion.
def orientation_filter(q, ang, acc):
	q0, q1, q2, q3 = q
	gx, gy, gz = ang
	ax, ay, az = acc

	q_dot_1 = 0.5 * (-q1 * gx - q2 * gy - q3 * gz)
	q_dot_2 = 0.5 * (q0 * gx + q2 * gz - q3 * gy)
	q_dot_3 = 0.5 * (q0 * gy - q1 * gz + q3 * gx)
	q_dot_4 = 0.5 * (q0 * gz + q1 * gy - q2 * gx)

	if not ((ax == 0.0) and (ay == 0.0) and (az == 0.0)):
		recip_norm = (ax * ax + ay * ay + az * az) ** (-0.5)
		ax *= recip_norm
		ay *= recip_norm
		az *= recip_norm

		_2q0 = 2.0 * q0
		_2q1 = 2.0 * q1
		_2q2 = 2.0 * q2
		_2q3 = 2.0 * q3
		_4q0 = 4.0 * q0
		_4q1 = 4.0 * q1
		_4q2 = 4.0 * q2
		_8q1 = 8.0 * q1
		_8q2 = 8.0 * q2
		q0q0 = q0 * q0
		q1q1 = q1 * q1
		q2q2 = q2 * q2
		q3q3 = q3 * q3

		s0 = _4q0 * q2q2 + _2q2 * ax + _4q0 * q1q1 - _2q1 * ay
		s1 = _4q1 * q3q3 - _2q3 * ax + 4.0 * q0q0 * q1 - _2q0 * ay - _4q1 + _8q1 * q1q1 + _8q1 * q2q2 + _4q1 * az
		s2 = 4.0 * q0q0 * q2 + _2q0 * ax + _4q2 * q3q3 - _2q3 * ay - _4q2 + _8q2 * q1q1 + _8q2 * q2q2 + _4q2 * az
		s3 = 4.0 * q1q1 * q3 - _2q1 * ax + 4.0 * q2q2 * q3 - _2q2 * ay

		recip_norm = (s0 * s0 + s1 * s1 + s2 * s2 + s3 * s3) ** (-0.5)
		s0 *= recip_norm
		s1 *= recip_norm
		s2 *= recip_norm
		s3 *= recip_norm

		q_dot_1 -= BETA_GAIN * s0
		q_dot_2 -= BETA_GAIN * s1
		q_dot_3 -= BETA_GAIN * s2
		q_dot_4 -= BETA_GAIN * s3

	q0 += q_dot_1 * (1.0 / SAMPLE_FREQ)
	q1 += q_dot_2 * (1.0 / SAMPLE_FREQ)
	q2 += q_dot_3 * (1.0 / SAMPLE_FREQ)
	q3 += q_dot_4 * (1.0 / SAMPLE_FREQ)

	recip_norm = (q0 * q0 + q1 * q1 + q2 * q2 + q3 * q3) ** (-1/2)
	q0 *= recip_norm
	q1 *= recip_norm
	q2 *= recip_norm
	q3 *= recip_norm

	return q0, q1, q2, q3
