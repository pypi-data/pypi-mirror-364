from . xwarning import warn, configure, WarningPrinter

if __name__ == '__main__':
	import sys
    
	# Simple usage you can use 'warn' similar as 'warning'
	warn("This is deprecated warning !", type="deprecated")
	print("\n")
	warn("This is user warning !", type="user")
	print("\n")
	warn("This is future warning !", type="future")
	print("\n")
	warn("This is runtime warning !", type="runtime")
	print("\n")
	warn("This is syntax warning !", type="syntax")
	print("\n")
	warn("This is import warning !", type="import")
	print("\n")
	warn("This is unicode warning !", type="unicode")
	print("\n")
	warn("This is general warning !", type="general")

	configure(show_icon=False, show_color=True)

	# Logging to file
	log_path = "warnings.log"
	configure(log_file=log_path)

	warn(f"This will go to the log file! with log file name '{log_path}'", type="user")

	log_path = True
	configure(log_file=log_path)
	warn(f"This will go to the log file! with log file name as bool in temp or /var/log directory", type="user")

	# Extra instance
	printer1 = WarningPrinter()
	printer1.configure(show_icon=False, log_file=True)
	printer1.warn("this user warning with printer1", type="user")

	printer2 = WarningPrinter()
	printer2.configure(show_icon=True, show_color=False)
	printer2.warn("this runtime warning with printer2", type="runtime")

	printer1.filterwarnings("ignore", category=UserWarning)

	printer1.warn("This will not appear as a user warning `filterwarning`", type="user")
	printer1.warn("This will appear as a runtime warning without `filterwarning`", type="runtime")
