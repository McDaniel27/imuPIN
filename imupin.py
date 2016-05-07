# imuPIN - imupin.py
# Stuart McDaniel, 2016

import pattern_recognition
import pins
import sensor
import sensor_samples
import utils

import tkinter
import tkinter.ttk


# Training window.
def training_open():
	# 'Record Feature' button.
	def record():
		directions_menu.configure(state="disabled")
		record_button.configure(state="disabled")
		log_textbox.configure(state="normal")
		root.update_idletasks()

		# Starting orientation quaternion.
		q = (1, 0, 0, 0)

		# Open serial port.
		log_textbox.insert(tkinter.INSERT, "Connecting to sensor...\n")
		root.update_idletasks()
		ser = sensor.open_serial_port()
		log_textbox.insert(tkinter.INSERT, "Sensor connected.\n")
		root.update_idletasks()

		# Calibrate sensor and get acceleration samples.
		log_textbox.insert(tkinter.INSERT, "Calibrating sensor...\n")
		root.update_idletasks()
		q = sensor_samples.calibrate_sensor_compare(ser, q, False, True)
		log_textbox.insert(tkinter.INSERT, "Sensor calibrated.\n")
		root.update_idletasks()
		log_textbox.insert(tkinter.INSERT, "Collecting sensor samples...\n")
		root.update_idletasks()
		q, raw_acceleration, angular_velocity, gravity, acceleration = sensor_samples.get_acceleration(ser, q, 500,
				False, True)
		log_textbox.insert(tkinter.INSERT, "Samples collected.\n")
		root.update_idletasks()

		# Close serial port.
		sensor.close_serial_port(ser)

		# Quantise acceleration samples.
		compressed = sensor_samples.quantise_compress(acceleration)

		# Extract key transitions features from acceleration.
		features = pattern_recognition.extract_features(compressed)

		# If extracted at least one feature.
		if len(features) >= 1:
			# Add training feature to training file.
			pattern_recognition.add_training_feature(features[0], selected_direction.get())
			log_textbox.insert(tkinter.INSERT, "Training feature added.\n")
			root.update_idletasks()

			delete_button.configure(state="normal")
			root.update_idletasks()
		else:
			log_textbox.insert(tkinter.INSERT, "No training feature recognised.\n")
			root.update_idletasks()

		log_textbox.configure(state="disabled")
		reset_button.configure(state="normal")
		root.update_idletasks()

	# 'Delete Feature' button.
	def delete():
		delete_button.configure(state="disabled")
		log_textbox.configure(state="normal")
		root.update_idletasks()

		# Delete last training feature from training file.
		pattern_recognition.delete_last_training_feature(selected_direction.get())
		log_textbox.insert(tkinter.INSERT, "Training feature deleted.\n")
		root.update_idletasks()

		log_textbox.configure(state="disabled")
		root.update_idletasks()

	# 'Reset' button.
	def reset():
		directions_menu.configure(state="normal")
		record_button.configure(state="normal")
		delete_button.configure(state="disabled")
		reset_button.configure(state="disabled")
		log_textbox.configure(state="normal")
		root.update_idletasks()

		log_textbox.delete("1.0", tkinter.END)
		root.update_idletasks()

		log_textbox.configure(state="disabled")
		root.update_idletasks()

	selected_direction = tkinter.StringVar()

	training_window = tkinter.Toplevel(root)
	training_window.resizable(0, 0)
	training_window.title("imuPIN: Training")

	main_frame = tkinter.ttk.Frame(training_window, padding=5)

	buttons_frame = tkinter.ttk.Frame(main_frame, padding=5)
	directions_frame = tkinter.ttk.Frame(buttons_frame)
	direction_label = tkinter.ttk.Label(directions_frame, text="Direction:")
	directions_menu = tkinter.ttk.OptionMenu(directions_frame, selected_direction, utils.DIRECTIONS[0], *utils.DIRECTIONS)
	record_button = tkinter.ttk.Button(buttons_frame, text="Record Feature", command=record)
	delete_button = tkinter.ttk.Button(buttons_frame, text="Delete Feature", command=delete, state="disabled")
	reset_button = tkinter.ttk.Button(buttons_frame, text="Reset", command=reset, state="disabled")

	log_frame = tkinter.ttk.Frame(main_frame, padding=5)
	log_textbox = tkinter.Text(log_frame, font="default 16", width=25, height=10, state="disabled")

	main_frame.pack()
	buttons_frame.pack()
	directions_frame.pack()
	direction_label.pack(side=tkinter.LEFT)
	directions_menu.pack(side=tkinter.LEFT)
	record_button.pack()
	delete_button.pack()
	reset_button.pack()
	log_frame.pack()
	log_textbox.pack()


# Classification logo.
def classification_open():
	# 'Generate PIN' button.
	def generate():
		global generated_pin

		generate_button.configure(state="disabled")
		log_textbox.configure(state="normal")
		root.update_idletasks()

		# Generate PIN between 0000 and 9999 based on PIN frequencies.
		generated_pin = pins.generate_frequency_pin("pin_files/pins.csv")
		log_textbox.insert(tkinter.INSERT, "Random PIN: " + generated_pin + "\n\n")
		root.update_idletasks()

		log_textbox.configure(state="disabled")
		record_button.configure(state="normal")
		root.update_idletasks()

	# 'Record PIN' button.
	def record():
		global generated_pin

		record_button.configure(state="disabled")
		log_textbox.configure(state="normal")
		root.update_idletasks()

		# Starting orientation quaternion.
		q = (1, 0, 0, 0)

		# Open serial port.
		log_textbox.insert(tkinter.INSERT, "Connecting to sensor...\n")
		root.update_idletasks()
		ser = sensor.open_serial_port()
		log_textbox.insert(tkinter.INSERT, "Sensor connected.\n")
		root.update_idletasks()

		# Calibrate sensor and get acceleration samples.
		log_textbox.insert(tkinter.INSERT, "Calibrating sensor...\n")
		root.update_idletasks()
		q = sensor_samples.calibrate_sensor_compare(ser, q, False, True)
		log_textbox.insert(tkinter.INSERT, "Sensor calibrated.\n")
		log_textbox.insert(tkinter.INSERT, "Collecting sensor samples...\n")
		root.update_idletasks()
		q, raw_acceleration, angular_velocity, gravity, acceleration = sensor_samples.get_acceleration(ser, q, 1000,
				False, True)
		log_textbox.insert(tkinter.INSERT, "Samples collected.\n\n")
		root.update_idletasks()

		# Close serial port.
		sensor.close_serial_port(ser)

		# Quantise acceleration samples.
		compressed = sensor_samples.quantise_compress(acceleration)

		# Get z-axis acceleration peaks.
		peaks = pattern_recognition.find_peaks(compressed, 2)

		# Segment PIN entry acceleration.
		segments = pattern_recognition.segment_pin_entry(compressed, peaks)

		# If found at least one segment.
		if len(segments) >= 1:
			# Extract key transition features from PIN entry segment.
			features = pattern_recognition.extract_features(segments[0])
			# Classify key transition features using k-NN classification algorithm and training features.
			transitions = pattern_recognition.classify_features(features, 5)
			log_textbox.insert(tkinter.INSERT, "PIN transition directions: " + transitions[0] + ", " + transitions[1] +
					", " + transitions[2] + "\n")
			# Get PINs that match key transition classes, in order of frequency.
			matching_pins = pins.get_matching_pins("pin_files/pins.csv", transitions)
			log_textbox.insert(tkinter.INSERT, "Matching PINs (in order of likelihood):\n")
			for pin in matching_pins:
				if pin == generated_pin:
					# Mark if found generated PIN.
					log_textbox.insert(tkinter.INSERT, pin + " *\n")
				else:
					log_textbox.insert(tkinter.INSERT, pin + "\n")
			root.update_idletasks()
		else:
			log_textbox.insert(tkinter.INSERT, "No PIN recognised.\n")
			root.update_idletasks()

		log_textbox.configure(state="disabled")
		reset_button.configure(state="normal")
		root.update_idletasks()

	# 'Reset' button.
	def reset():
		generate_button.configure(state="normal")
		reset_button.configure(state="disabled")
		log_textbox.configure(state="normal")
		root.update_idletasks()

		log_textbox.delete("1.0", tkinter.END)
		root.update_idletasks()

		log_textbox.configure(state="disabled")
		root.update_idletasks()

	generated_pin = ""

	classification_window = tkinter.Toplevel(root)
	classification_window.resizable(0, 0)
	classification_window.title("imuPIN: Classification")

	main_frame = tkinter.ttk.Frame(classification_window, padding=5)

	buttons_frame = tkinter.ttk.Frame(main_frame, padding=5)
	generate_button = tkinter.ttk.Button(buttons_frame, text="Generate PIN", command=generate)
	record_button = tkinter.ttk.Button(buttons_frame, text="Record PIN", command=record, state="disabled")
	reset_button = tkinter.ttk.Button(buttons_frame, text="Reset", command=reset, state="disabled")

	log_frame = tkinter.ttk.Frame(main_frame, padding=5)
	log_textbox = tkinter.Text(log_frame, font="default 16", width=28, height=18, state="disabled")
	log_scrollbar = tkinter.ttk.Scrollbar(log_frame)
	log_textbox.config(yscrollcommand=log_scrollbar.set)
	log_scrollbar.config(command=log_textbox.yview)

	main_frame.pack()
	buttons_frame.pack()
	generate_button.pack()
	record_button.pack()
	reset_button.pack()
	log_frame.pack()
	log_textbox.pack(side=tkinter.LEFT)
	log_scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y, expand=False)

root = tkinter.Tk()
root.resizable(0, 0)
root.title("imuPIN")
menu_bar = tkinter.Menu(root)
root.configure(menu=menu_bar)

s = tkinter.ttk.Style()
s.configure("TLabel", font="default 16", justify="center", padding=5)
s.configure("TButton", font="default 18", padding=5)
s.configure("Home.TButton", font="default 22", padding=5)

main_frame = tkinter.ttk.Frame(root, padding=5)

logo_frame = tkinter.ttk.Frame(main_frame, padding=5)
logo_image = tkinter.PhotoImage(file="media/logo.gif")
logo_label = tkinter.ttk.Label(logo_frame, image=logo_image)

buttons_frame = tkinter.ttk.Frame(main_frame, padding=5)
training_button = tkinter.ttk.Button(buttons_frame, style="Home.TButton", text="Training", command=training_open)
classification_button = tkinter.ttk.Button(buttons_frame, style="Home.TButton", text="Classification",
		command=classification_open)

main_frame.pack()
logo_frame.pack()
logo_label.pack()
buttons_frame.pack()
training_button.pack(side=tkinter.LEFT)
classification_button.pack(side=tkinter.LEFT)

root.mainloop()
