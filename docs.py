import io


class DocWriter:
	
	def __init__(self):
		self._io = io.StringIO()
		self._l = 0
	
	def writeline(self, s):
		self._io.write((' ' * self._l) + s + '\n')
		return self
	
	def newline(self):
		self._io.write('\n')
		return self
	
	def write(self, s):
		self._io.write((' ' * self._l) + s)
		return self
	
	def __enter__(self):
		self._l += 1
	
	def __exit__(self, exc_type, exc_val, exc_tb):
		self._l -= 1
	
	def __add__(self, other):
		self._l += other
	
	def __sub__(self, other):
		self._l -= other
	
	def tab(self):
		self._l += 1
		return self
	
	def untab(self):
		self._l -= 1
		return self
	
	@property
	def level(self):
		return self._l
	
	def getvalue(self):
		return self._io.getvalue()

_PROJECT_HELP_ITEMS = \
[
	DocWriter()
	.writeline("project <project dir>")
	.tab()
	.writeline("[!REQUIRED!]")
	.writeline("The project directory path")
	.writeline("Replaces every instances of '__proj__' in later paths/define values")
	.getvalue(),
	
	DocWriter()
	.writeline("source <source dir>")
	.tab()
	.writeline("[!REQUIRED!]")
	.writeline("The directory conatining you headers")
	.writeline("Replaces every instances of '__src__' in later paths/define values")
	.getvalue(),
	
	DocWriter()
	.writeline("output <output dir>")
	.tab()
	.writeline("[!REQUIRED!]")
	.writeline("The directory where libraries/headers/binaries will be deploied")
	.writeline("Replaces every instances of '__out__' in later paths/define values")
	.getvalue(),
	
	DocWriter()
	.writeline("include_dir <include dir>")
	.tab()
	.writeline("If not set, the defualt will be '__out__\\include'")
	.writeline("all headers will be deploied to this path")
	.getvalue(),
	
	DocWriter()
	.writeline("blacklist <header filepath regex> [, *<flags>]")
	.tab()
	.writeline("puts the regex into the blacklist")
	.writeline("Note: if the blacklist is inverted after this command; the blacklisted header will be whitelisted")
	.writeline("Note: this uses REGEX and all the list is tested against the filepath.")
	.writeline("FLAGS:")
	.tab()
	.writeline("/s, /ignorecase        -> Ignore case")
	.writeline("/S, /-ignorecase, /-s  -> case-sensitive")
	.writeline("/d, /dotall            -> the '.' matchs newlines")
	.writeline("/D, /-dotall, /-d      -> the '.' never matchs a newline")
	.writeline("/m, /multiline         -> '$' and '^' anchors anchor to newlines")
	.writeline("/M, /-multiline, /-m   ->  '$' and '^' anchors only anchor to end/start of the pattren")
	.getvalue(),
	
	
	DocWriter()
	.writeline("whitelist <header filepath regex> [, *<flags>]")
	.tab()
	.writeline("puts the regex into the whitelist")
	.writeline("Note: if the whitelist is inverted after this command; the whitelist header will be blacklisted")
	.writeline("Note: this uses REGEX and all the list is tested against the filepath.")
	.writeline("FLAGS:")
	.tab()
	.writeline("/s, /ignorecase        -> Ignore case")
	.writeline("/S, /-ignorecase, /-s  -> case-sensitive")
	.writeline("/d, /dotall            -> the '.' matchs newlines")
	.writeline("/D, /-dotall, /-d      -> the '.' never matchs a newline")
	.writeline("/m, /multiline         -> '$' and '^' anchors anchor to newlines")
	.writeline("/M, /-multiline, /-m   ->  '$' and '^' anchors only anchor to end/start of the pattren")
	.getvalue(),
	
	DocWriter()
	.writeline("copy <src path> <dst path> [, /o, /overwrite] [, /s, /silent]")
	.tab()
	.writeline("A copy command from the src path to the dst path.")
	.writeline("the switch '/o' or '/overwrite' makes the copy overwrite the destination")
	.writeline("the switch '/s' or '/silent' makes the copy silently handle some errors (e.g. when the source doesn't exist)")
	.getvalue(),
	
	DocWriter()
	.writeline("move <src path> <dst path> [, /o, /overwrite] [, /s, /silent]")
	.tab()
	.writeline("A move command from the src path to the dst path.")
	.writeline("the switch '/o' or '/overwrite' makes the move overwrite the destination")
	.writeline("the switch '/s' or '/silent' makes the move silently handle some errors (e.g. when the source doesn't exist)")
	.getvalue(),
	
	DocWriter()
	.writeline("delete <target path> [, /o, /overwrite] [, /s, /silent]")
	.tab()
	.writeline("A rename command renames the src files/folder to new_name.")
	.writeline("the switch '/o' or '/overwrite' has no effects in delete actions")
	.writeline("the switch '/s' or '/silent' makes the delete silently handle some errors (currently it has no effects)")
	.getvalue(),
	
	DocWriter()
	.writeline("invert_blacklist")
	.tab()
	.writeline("inverts the blacklist to a whitelist and vaisversa")
	.getvalue(),
	
	DocWriter()
	.writeline("include_file_type <file extension (without the '.')>")
	.tab()
	.writeline("Treats all file of this extension like headers.")
	.getvalue(),
	
	DocWriter()
	.writeline("define:<name> <value>")
	.tab()
	.writeline("Defines <name> with <value>, any instance of '__<name>__' in any path is replaced by '<value>'.")
	.writeline("For examble: --define:output __proj__\\win64.")
	.getvalue(),
]


def _get_summary():
	s = DocWriter()
	
	# presentation:
	s.write('#' * 64 + '\n')
	s.write("\tHiveC" + '\n')
	s.write("\tMade by Bezar" + '\n')
	s.write("\tAll rights (C) 2023 reserved for Zaher abdolatif abdorab babakr (Bezar/BotatoDev)" + '\n')
	s.write('#' * 64 + '\n\n')
	
	s.write("Summary:" + '\n')
	s.write("\tLib deploy is a simple script to help deploy script using command-line arguments passed to the script" + '\n')
	s.write("\tYou can custmize the deploying process in many ways to be the best for your coding enviorment!" + '\n')
	s.write("\n")
	s.write("\tFor Any suggesting, make an issue on githup (githup.com\BezarHere)" + '\n')

	return s.getvalue()

def _get_filemode_help(long: bool = False):
	s = DocWriter()
	
	s.writeline("File mode [, /f]:")
	
	s.tab()
	s.writeline("Deploying project using the given Hivec args file")
	if long:
		s.writeline("making the first argument a valid file path or puting '/f' as first argument")
		s.writeline("if Hivec detected file mode; all commandline arguments are processed as filepaths")
		s.writeline("so putting multible filepaths will load and excute all said filepaths")
	# s.writeline("Expected file should be with name 'hivec.args' if no file is specified")
	s.untab()
	
	return s.getvalue()

def _get_clmode_help(long: bool = False):
	s = DocWriter()
	
	s.writeline("[!DEPRTICATED!]Command-line mode [/c]:")
	
	s.tab()
	s.writeline("Deploying project using command line arguments")
	if long:
		s.writeline("given the huge constraints of the command line, and with further")
		s.writeline("leaning to args files, the command-line mode will be soon removed")
	s.untab()
	
	return s.getvalue()

def _get_new_help(long: bool = False):
	s = DocWriter()
	
	s.writeline("New [new]:")
	
	s.tab()
	s.writeline("Creats a new hivec project (.args)")
	if long:
		s.writeline("if any filepath is given after the 'new' command, the new project file")
		s.writeline("will be created at said filepath, otherwise, the new project file")
		s.writeline("will be created '<working directory>\\hivec.args'")
	s.untab()
	
	return s.getvalue()

def _get_show_help(long: bool = False):
	s = DocWriter()
	
	s.writeline("Show [show]:")
	
	s.tab()
	s.writeline("Prints out information about the hivec project (.args)")
	if long:
		s.writeline("if any filepath is given after the 'show' command, the project file")
		s.writeline("at said path will be read, processed but not executed, it will (instad) print out")
		s.writeline("to the stdout as digestive information about the hivec project")
	s.untab()
	
	return s.getvalue()
	

def _get_commands_help(long: bool = False):
	s = DocWriter()
	
	s.writeline(_get_filemode_help(long))
	s.writeline(_get_clmode_help(long))
	s.writeline(_get_new_help(long))
	s.writeline(_get_show_help(long))
	
	return s.getvalue()

def _get_project_struct_help():
	s = DocWriter()
	
	for i in _PROJECT_HELP_ITEMS:
		s.writeline(i)
	
	return s.getvalue()

def gen_help():
	s = DocWriter()
	
	s.writeline(_get_summary())
	
	s.writeline(_get_commands_help(True))
	
	s.writeline(_get_project_struct_help())
	
	return s.getvalue()


