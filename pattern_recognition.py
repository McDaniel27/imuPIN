# imuPIN - pattern_recognition.py
# Stuart McDaniel, 2016

import utils

import numpy
import os
import peakutils
import pickle
import scipy.interpolate
import sklearn.neighbors


# Get ?-axis acceleration peaks.
def find_peaks(acceleration, peaks_axis):
	return peakutils.peak.indexes(numpy.array(acceleration[peaks_axis]), thres=0.25, min_dist=10)


# Segment PIN entry acceleration.
def segment_pin_entry(acceleration, peaks):
	segments = []

	# If enough z-axis acceleration peaks for PIN entry.
	if len(peaks) >= 4:
		# For each sequence of four peaks.
		for i in range(len(peaks) - 3):
			# Create and normalise possible PIN entry segment.
			# [2, 4, 6, 8] becomes [0, 2, 4, 6].
			possible_segment = list(peaks[i:i + 4])
			for j in range(3, -1, -1):
				possible_segment[j] -= possible_segment[0]

			# Add segment if peaks relatively equidistant.
			segment_length = possible_segment[3] - possible_segment[0]
			if 0.21 <= (possible_segment[1] / segment_length) <= 0.45:
				if 0.54 <= (possible_segment[2] / segment_length) <= 0.78:
					segments.append((list(acceleration[0][peaks[i] - 2:peaks[i + 3] + 3]),
							list(acceleration[1][peaks[i] - 2:peaks[i + 3] + 3]),
							list(acceleration[2][peaks[i] - 2:peaks[i + 3] + 3])))

	return segments


# Extract key transition features from acceleration.
def extract_features(acceleration):
	# Get z-axis acceleration peaks.
	peaks = find_peaks(acceleration, 2)

	# Extract acceleration between peaks.
	features = []
	for i in range(len(peaks) - 1):
		feature = (list(acceleration[0][peaks[i] + 1:peaks[i + 1]]),
				list(acceleration[1][peaks[i] + 1:peaks[i + 1]]),
				list(acceleration[2][peaks[i] + 1:peaks[i + 1]]))
		# Change number of samples in feature using linear interpolation.
		features.append(resample_feature(feature, utils.FEATURE_SIZE))

	return features


# Change number of samples in feature using linear interpolation.
def resample_feature(feature, new_size):
	# Number of samples in feature.
	sample_numbers = range(len(feature[0]))

	# Resample each axis of feature using linear interpolation.
	resampled_feature = [], [], []
	for i in range(3):
		# Calculate function of axis.
		function = scipy.interpolate.interp1d(sample_numbers, feature[i])
		# Calculate new samples using axis function.
		for j in range(new_size):
			resampled_feature[i].append(float(function(j / (new_size - 1) * (len(feature[i]) - 1))))

	return resampled_feature


# Add training feature to training file.
def add_training_feature(feature, direction_class):
	# Get training features from training file.
	training_features = []
	if os.path.isfile("training_files/" + direction_class + ".pkl"):
		with open("training_files/" + direction_class + ".pkl", "rb") as features_file:
			training_features = pickle.load(features_file)

	# Add new feature to training features.
	training_features.append(numpy.reshape(feature, -1))

	# Write training features to training file.
	with open("training_files/" + direction_class + ".pkl", "wb") as features_file:
		pickle.dump(training_features, features_file)


# Delete last training feature from training file.
def delete_last_training_feature(direction_class):
	# Get training features from training file.
	training_features = []
	if os.path.isfile("training_files/" + direction_class + ".pkl"):
		with open("training_files/" + direction_class + ".pkl", "rb") as features_file:
			training_features = pickle.load(features_file)

	# Remove last training feature.
	training_features.pop()

	# Write training features to training file.
	with open("training_files/" + direction_class + ".pkl", "wb") as features_file:
		pickle.dump(training_features, features_file)


# Get training features from training files.
def get_training_features():
	# For each key transition class, open file and get each training feature and name of class.
	training_features = []
	direction_classes = []
	for direction in utils.DIRECTIONS:
		with open("training_files/" + direction + ".pkl", "rb") as features_file:
			class_features = pickle.load(features_file)
			for class_feature in class_features:
				training_features.append(class_feature)
				direction_classes.append(direction)

	return training_features, direction_classes


# Classify key transition features using k-NN classification algorithm and training features.
def classify_features(features, k):
	# Create k-NN classification algorithm.
	knn = sklearn.neighbors.KNeighborsClassifier(n_neighbors=k)

	# Get training features and names of classes from training files.
	training_features, direction_classes = get_training_features()

	# Add training data to k-NN classification algorithm.
	knn.fit(numpy.asarray(training_features), numpy.asarray(direction_classes))

	# Classify features using k-NN classification algorithm.
	return knn.predict([numpy.reshape(features[0], -1), numpy.reshape(features[1], -1),
			numpy.reshape(features[2], -1)])
