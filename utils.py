# imuPIN - utils.py
# Stuart McDaniel, 2016

import datetime
import numpy
import os


# Create and open folder to save sensor data and graphs in.
def create_folder():
	folder_name = str(datetime.datetime.now().strftime("%Y-%m-%d %H%M%S"))
	os.makedirs(folder_name)
	os.chdir(folder_name)


# Calculate if values in list of tuples are within certain range of each other.
def within_range(tuples, range_value):
	within = True
	for i in range(len(tuples) - 1):
		for j in range(i + 1, len(tuples)):
			if abs(tuples[i][0] - tuples[j][0]) > range_value or abs(tuples[i][1] - tuples[j][1]) > range_value or \
					abs(tuples[i][2] - tuples[j][2]) > range_value:
				within = False

	return within


# Convert list of (x, y, z) tuples into array of arrays of x, y, and z values.
# [(1, 2, 3), (4, 5, 6)] becomes {{1, 4}, {2, 5}, {3, 6}}
def convert_tuples(tuples):
	arrays = numpy.empty((3, len(tuples)))
	for i in range(len(tuples)):
		arrays[0][i] = tuples[i][0]
		arrays[1][i] = tuples[i][1]
		arrays[2][i] = tuples[i][2]

	return arrays
