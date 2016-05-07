# imuPIN - utils.py
# Stuart McDaniel, 2016

import datetime
import os

# SYSTEM CONSTANTS.
# Serial port name.
SERIAL_PORT = "/dev/cu.WAX9-DCDD-COM1"
# Sample frequency of sensor in Hz.
SAMPLE_FREQ = 100.0
# Number of samples in sliding window.
WINDOW_SIZE = 5
# Number of samples sliding window slides.
WINDOW_SLIDE = 3
# Number of samples in resampled features.
FEATURE_SIZE = 30
# Keypad number co-ordinates.
# For keypad of layout:
# 1 2 3
# 4 5 6
# 7 8 9
#   0
KEYPAD = (1, 0), (0, 3), (1, 3), (2, 3), (0, 2), (1, 2), (2, 2), (0, 1), (1, 1), (2, 1)
# Keypad transition direction classes.
DIRECTIONS = ["L", "R", "D", "U", "LD", "LU", "RD", "RU", "S"]


# Create and open folder to save sensor data in.
def create_folder():
	os.chdir("sensor_data")
	folder_name = str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
	os.makedirs(folder_name)
	os.chdir(folder_name)


# Calculate if values in lists within certain range of each other.
def list_within_range(lists, range_value):
	for i in range(len(lists[0]) - 1):
		for j in range(i + 1, len(lists[0])):
			if abs(lists[0][i] - lists[0][j]) > range_value or abs(lists[1][i] - lists[1][j]) > range_value or \
					abs(lists[2][i] - lists[2][j]) > range_value:
				return False

	return True
