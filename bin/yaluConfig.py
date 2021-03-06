#!/usr/bin/python
 ##############################################################################
################################################################################
####            YetAnotherLevelUp (YALU), an FVWM Configuration             ####
####               ~ Jonathan Heathcote                                     ####
####               ~ September 2009 - Present                               ####
####               ~ GNU GPLv3                                              ####
################################################################################
 ##############################################################################
# yaluConfig:
#   Facilitates setting options in the config file. Syntax:
#      yaluConfig option [value]
#   If no value is specified the current value, default and possible values are
#   printed. If 'defaults' is supplied as an option a minimal config-file
#   containing the defaults is printed.

import sys, os, commands, re

################################################################################
# Possible option values                                                       #
#   This dictionary is used by the Option class to provide default values and  #
#   possible option values. The format of the entries in the dictionary is as  #
#   follows:                                                                   #
#   {                                                                          #
#      " default": " defaultValue",                                            #
#      "values": [ (label, value), None,... ],                                 #
#      "directories": [ "dirName", None,... ]                                  #
#   }                                                                          #
#   All values are strings. If a value is set to None the user will be         #
#   prompted with a graphical dialogue offering to select a custom value. A    #
#   custom prompt can be specified by adding a third element to the tuple. If  #
#   a label/value pair is replaced with None a seperator is inserted. If       #
#   directories is set then a list of directories to list the files in is      #
#   specified.                                                                 #
################################################################################

yaluOptions = {
	"Editor" : {
		"default": "gvim",
		"values": [
			("GVim", "gvim"),
			("Emacs", "emacs"),
			("Emacs Client", "emacsclient"),
			None,
			("NEdit", "nedit"),
			("gedit", "gedit"),
			("KATE", "kate"),
			None,
			("Custom", None, "Please enter your choice of graphical text editor."),
		]
	},
	"Terminal" : {
		"default": "xterm",
		"values": [
			("xterm", "xterm"),
			None,
			("Gnome Terminal", "gnome-terminal"),
			("Konsole", "konsole"),
			None,
			("aterm", "aterm"),
			("eterm", "eterm"),
			("rxvt", "rxvt"),
			None,
			("Custom", None, "Please enter your choice of terminal emulator."),
		]
	},
	"Browser" : {
		"default": "firefox",
		"values": [
			("FireFox", "firefox"),
			None,
			("Konqueror", "konqueror"),
			("Epiphany", "epiphany"),
			None,
			("Google Chrome", "google-chrome"),
			("Chromium", "chromium"),
			("Opera", "opera"),
			None,
			("Custom", None, "Please enter your choice of web browser."),
		]
	},
	"FocusMode" : {
		"default": "MouseFocus",
		"values": [
			("Click To Focus (Windows Style)", "ClickToFocus"),
			("Focus Follows Mouse (FVWM Style)", "MouseFocus"),
			("Sloppy Focus (X Style)", "SloppyFocus"),
		]
	},
	"PlaceMode" : {
		"default": "MinOverlapPlacement",
		"values": [
			("Tile if possible, then cascade", "TileCascadePlacement"),
			("Tile if possible, then manually place", "TileManualPlacement"),
			("Place all windows manually", "ManualPlacement"),
			("Tile with as little overlap as possible", "MinOverlapPlacement"),
			("Tile with as little % overlap as possible", "MinOverlapPercentPlacement"),
		]
	},
	"SnapDistance" : {
		"default": 10,
		"values": [ ("Disabled", 0), ] + [
			("%ipx"%(x,), x) for x in range(1, 11)
		] + [
			("%ipx"%(x,), x) for x in range(15, 26, 5)
		] + [
			("%ipx"%(x,), x) for x in range(50, 201, 50)
		] + [
			None,
			("Custom", None, "How many px should the snapping distance be?")
		]
	},
	"ResizeCorner" : {
		"default": "WarpToWindow 100% 100%",
		"values": [
			("Cursor", ""),
			("Top-Left", "WarpToWindow 0% 0%"),
			("Top-Right", "WarpToWindow 100% 0%"),
			("Bottom-Left", "WarpToWindow 0% 100%"),
			("Bottom-Right", "WarpToWindow 100% 100%"),
		]
	},
	"Desks" : {
		"default": 0,
		"values": [ (str(x+1), x) for x in range(5) ] + [
			None,
			("Custom", None, "How many desks would you like?")
		]
	},
	"DeskWidth" : {
		"default": 3,
		"values": [ (str(x), x) for x in range(1,6) ] + [
			None,
			("Custom", None, "How many pages wide should each desk be?")
		]
	},
	"DeskHeight" : {
		"default": 2,
		"values": [ (str(x), x) for x in range(1,6) ] + [
			None,
			("Custom", None, "How many pages high should each desk be?")
		]
	},
	"EdgeJumpWidth" : {
		"default": 100,
		"values": [ ("Disabled", 0) ] + [
			("%i%%"%(x,), x) for x in range(10,101, 10)
		] + [
			None,
			("Custom", None, "What percentage of the screen's width should the screen jump by?")
		]
	},
	"EdgeJumpHeight" : {
		"default": 100,
		"values": [ ("Disabled", 0) ] + [
			("%i%%"%(x,), x) for x in range(10,101, 10)
		] + [
			None,
			("Custom", None, "What percentage of the screen's height should the screen jump by?")
		]
	},
	"EdgeResistDelay" : {
		"default": 0,
		"values": [ ("None", 0) ] + [
			("%2.1fs"%(x/1000.0,), x) for x in range(100,1001, 100)
		] + [
			None,
			("Custom", None, "How long should the delay (in ms) be before the screen changes page?")
		]
	},
	"DelayExitTime" : {
		"default": 30,
		"values": [
			("Do not keep", 0),
		] + [ ("%isecs"%(x,), x) for x in range(5, 21, 5) + range(30, 60, 10)] + [
			("1min", 60),
			("2mins", 2*60),
			("5mins", 5*60),
			None,
			("Custom", None, "How long (secs) should the terminal stay active after a program exits?")
		]
	},
	"ExecHistoryType" : {
		"default": "frequent",
		"values": [
			("Frequently Used", "frequent"),
			("Recently Used", "recent"),
		]
	},
	"WindowTypeColours" : {
		"default": "",
		"values": [
			("Enabled", ""),
			("Disabled", "Nop"),
		]
	},
	"ImageType" : {
		"default": "png",
		"values": [
			("High-Quality (PNG)", "png"),
			("Low-Quality (XPM)", "xpm"),
		]
	},
	"Theme" : {
		"default": os.path.join(os.environ["YALU"], "themes", "default"),
		"directories": [
			"%s/themes/"%(os.environ["LocalYALU"],),
			None,
			"%s/themes/"%(os.environ["YALU"],),
		]
	},
	"AutoRaise" : {
		"default": "-1",
		"values": [
			("Disabled", "-1"),
			None,
		] + [
			(
				"%1.1fsecs"%(x/10.0,), str(x*100)
			) for x in range(0, 11, 1)
		]
	},
} # yaluOptions {}

################################################################################
# Option file interface.                                                       #
################################################################################

def FvwmCommand(command):
	command = command.replace("\"","\\\"")
	commands.getoutput("FvwmCommand \"%s\""%("Echo " + command,))
	commands.getoutput("FvwmCommand \"%s\""%(command,))

class OptionDoesNotExist(Exception):
	pass

class Option(object):
	"""A representation and interface to a yalu config file option."""
	def __init__(self, name, configFile="yaluConfig"):
		"""
		optionName: A valid YALU option name.
		configFile: The config file to write settings to
		"""
		self.name = name
		self.configFile = configFile
		# Ensure the option is valid (i.e. listed in yaluOptions)
		global yaluOptions
		if name not in yaluOptions:
			raise OptionDoesNotExist()
		
		self.default = str(yaluOptions[name]["default"])
	
	def getValues(self):
		global yaluOptions
		if yaluOptions[self.name].has_key("values"):
			return yaluOptions[self.name]["values"]
		elif yaluOptions[self.name].has_key("directories"):
			values = []
			print yaluOptions[self.name]["directories"]
			for directory in yaluOptions[self.name]["directories"]:
				if directory != None:
					try:
						values.extend([
							(filename, os.path.join(directory, filename)) for filename in os.listdir(directory)
						])
					except:
						pass
				else:
					values.append(None)
			return values
	
	values = property(getValues)
	
	def getValue(self):
		try:
			return os.environ["yalu%s"%(self.name,)]
		except KeyError:
			return ""
	
	def getConfigLine(self, value):
		return "SetEnv yalu%s \"%s\""%(self.name, value)
	
	def setValue(self, value):
		# Load the config file (and store line-by-line)
		config = open(self.configFile, "r").read()
		
		# Generate the new environment variable line
		newConfigLine = self.getConfigLine(value)
		
		# Check the file for the matching envvar and update it
		regex = "SetEnv\s+yalu%s.*"%(self.name,)
		config, noOfReplacements = re.subn(regex, newConfigLine, config)
		
		if noOfReplacements == 0:
			config += "\n# Added automatically by yaluConfig.py\n"
			config += "%s\n"%(newConfigLine,)
		
		# Send Fvwm command to set variable
		FvwmCommand(newConfigLine)
		
		# Run the yalu updating scripts to apply the change
		FvwmCommand("set%s"%(self.name,))
		
		# Save the new config
		open(self.configFile, "w").write(config)
	value = property(getValue,setValue)

################################################################################
# Commandline behaviour.                                                       #
################################################################################

if __name__ == "__main__":
	# Move into the YALU dir so that all paths from now on can be relative
	os.chdir(os.environ["LocalYALU"])
	
	# Check that a config file exists (if not, create it)
	try:
		open("yaluConfig", "r")
	except IOError:
		open("yaluConfig", "w").write(
			"# See yaluConfig.example for help on editing this file or use the YALU menu\n"
		)
	
	
	if len(sys.argv) == 1:
		print "'printAllDefaults' or..."
		print "Available options:"
		for option in yaluOptions:
			print option
	elif len(sys.argv) == 2 and sys.argv[1] == "printAllDefaults":
		for option in yaluOptions:
			opt = Option(option)
			print opt.getConfigLine(opt.default)
	elif len(sys.argv) == 2:
		selectedOption = Option(sys.argv[1])
		print selectedOption.value
		print "Default:", selectedOption.default
	elif len(sys.argv) == 3:
		selectedOption = Option(sys.argv[1])
		selectedOption.value = str(sys.argv[2])
	else:
		sys.stderr.write("Invalid arguments\n")
		sys.stderr.write("Usage: yaluConfig [optionName [newValue]]\n")
