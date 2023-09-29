"""
All rights (C) 2023 reserved for Zaher abdolatif abdorab babakr (Bezar/BotatoDev)
"""
import enum
import glassy.utils
import os
import re
import sys
from glassy.utils import Tape
from pathlib import Path

from _hivefile import Request, Action, ActionType, PathPipe

async_mode: bool = False

_verbose: bool = False

class RunMode(enum.IntEnum):
	NoMode = 0
	FileArgs = 1
	CommandLineArgs = 2
	
	@property
	def name(self):
		return ('no mode', 'args file mode', 'command line args mode')[int(self)]

def print_general_help():
	level: int = 1
	show = lambda s: print('  ' * level, s)
	
	# presentation:
	print('#' * 64)
	print("\tHiveCPP")
	print("\tMade by Bezar")
	print("\tAll rights (C) 2023 reserved for Zaher abdolatif abdorab babakr (Bezar/BotatoDev)")
	print('#' * 64)
	
	print("Summary:")
	print("\tLib deploy is a simple script to help deploy script using command-line arguments passed to the script")
	print("\tYou can custmize the deploying process in many ways to be the best for your coding enviorment!")
	print("")
	print("\tFor Any suggesting, make an issue on githup (githup.com\BezarHere)")
	print()
	
	print("Usages:")
	
	print()
	
	level -= 1
	show("/f <args file path>")
	level += 1
	show("Runs the argument file, Should be always the first argument.")
	show("no more argument from the commandline will be read if this switch is present.")
	show("[DEFAULT] if the first argument is a valid hive arguments file")
	
	print()
	
	level -= 1
	show("/s")
	level += 1
	show("Directs the input from the successiding commandline arguments")
	
	show("[REQUIRED] source <source path>")
	level += 1
	show("Where is the source code (headers)?")
	show("The folder where all the headers will be loaded.")
	show("The source path replaces every '__src__' in other paths.")
	
	print()
	
	level -= 1
	show("[REQUIRED] output <output path>")
	level += 1
	show("Where will build lib be at?")
	show("The folder where all the headers (\\include), libraries (\\lib) and binaries (\\bin) will be deployied.")
	show("The include path replaces every '__out__' in other paths.")
	
	print()
	
	level -= 1
	show("[REQUIRED] project <project path>")
	level += 1
	show("Where is the project?")
	show("The project path replaces every '__proj__' in other paths.")
	
	print()
	
	level -= 1
	show("copy <src path> <dst path> [, /o, /overwrite] [, /s, /silent]")
	level += 1
	show("A copy command from the src path to the dst path.")
	show("the switch '/o' or '/overwrite' makes the copy overwrite the destination")
	show("the switch '/s' or '/silent' makes the copy silently handle some errors (e.g. when the source doesn't exist)")
	
	print()
	
	level -= 1
	show("move <src path> <dst path> [, /o, /overwrite] [, /s, /silent]")
	level += 1
	show("A move command from the src path to the dst path.")
	show("the switch '/o' or '/overwrite' makes the move overwrite the destination")
	show("the switch '/s' or '/silent' makes the move silently handle some errors (e.g. when the source doesn't exist)")
	
	print()
	
	level -= 1
	show("rename <src path> <new_name> [, /o, /overwrite] [, /s, /silent]")
	level += 1
	show("A rename command renames the src files/folder to new_name.")
	show("the switch '/o' or '/overwrite' makes the rename overwrite any other files with the new name")
	show("the switch '/s' or '/silent' makes the rename silently handle some errors (e.g. when the source doesn't exist or if there is a name collision without the overwrite switch)")
	
	print()
	
	level -= 1
	show("delete <target path> [, /o, /overwrite] [, /s, /silent]")
	level += 1
	show("A rename command renames the src files/folder to new_name.")
	show("the switch '/o' or '/overwrite' has no effects in delete actions")
	show("the switch '/s' or '/silent' makes the delete silently handle some errors (currently it has no effects)")
	
	print()
	
	level -= 1
	show("ignore <header file>")
	level += 1
	show("Ingnores a header from transfering (deploying) to the include folder.")
	
	print()
	
	level -= 1
	show("include_file_type <file extension (without the '.')>")
	level += 1
	show("Treats all file of this extension like headers.")
	
	print()
	
	level -= 1
	show("define:<name> <value>")
	level += 1
	show("Defines <name> with <value>, any instance of '__<name>__' in any path is replaced by '<value>'.")
	show("For examble: --define:output __proj__\\win64")
	


def print_help(subject: str):
	if not subject:
		print_general_help()
		return


def _proc_args_line(line: str):
	line = line.strip()
	if not line and line[0] == '#':
		return ''
	return line.strip('"')

# stdout = sys.stdout.seek()

def pipin_args(args_path: Path):
	if not args_path.exists():
		print(f"ERROR: No arguments file found at '{args_path}'/'{args_path.absolute()}'")
		return list()
	
	with open(args_path, 'r', encoding='utf-8') as f:
		text = f.read()
	
	lines_col = (i.strip() for i in text.splitlines() if i.strip())
	
	args = []
	
	for line in lines_col:
		for i in glassy.utils.to_args(line):
			if i == '#':
				break
			args.append(i)
	
	return args

def get_include_file_types_default(for_lang: str):
	match for_lang:
		case "c":
			return 'h', 'inl'
		case "c++":
			return 'h', 'hpp', 'hxx', 'inl'
	return tuple()

def _parse_action_switchs(args: Tape[str]):
	if args.peek() == '/o' or args.peek() == '/overwrite':
		args.read()
		if args.peek() == '/s' or args.peek() == '/silent':
			args.read()
			return True, True
		return True, False
	
	if args.peek() == '/s' or args.peek() == '/silent':
		args.read()
		return False, True
	
	return False, False
	

def generate_request_from_args(args: Tape[str], working_path: Path):
	found_src_folder: bool = False
	found_out_folder: bool = False
	working_path.resolve()
	working_path_str = str(working_path).strip('\\').strip('/')
	
	def read_path():
		s = args.read().strip().strip('"')
		if len(s) > 2 and s[:2] == '..':
			s = working_path_str + s[2:]
		return Path(s)
	
	project_path: Path = Path()
	src_folder: Path = Path()
	output_folder: Path = Path()
	
	ignored_src_files_regex: set[re.Pattern] = set()
	actions: list[Action] = list[Action]()
	custom_path_defines: dict[str, str] = dict[str, str]()
	include_file_types: set[str] = set[str]()
	
	override_include_folder: bool = True
	strict: bool = False
	
	while args:
		t = args.read()
		
		# paramter
		if t[0] == '-' and t[1] == '-':
			t = t[2:].lower()
			
			if t == "keep-inc" or t == "keep-includes":
				override_include_folder = False
			
		# strict
		elif t == '/S':
			strict = True
		# live
		elif t == '/l':
			live = True
		elif t == 'copy':
			pipe = PathPipe((read_path(), read_path()))
			overwrite, silent = _parse_action_switchs(args)
				
			actions.append(
				Action(ActionType.Copy if overwrite else ActionType.Copy, pipe, silent)
			)
		
		elif t == 'move':
			pipe = PathPipe((read_path(), read_path()))
			overwrite, silent = _parse_action_switchs(args)
				
			actions.append(
				Action(ActionType.Move if overwrite else ActionType.MoveNoOverwrite, pipe, silent)
			)
		
		elif t == 'rename':
			pipe = PathPipe((read_path(), read_path()))
			overwrite, silent = _parse_action_switchs(args)
			
			actions.append(
				Action(ActionType.RenameOverwrite if overwrite else ActionType.Rename, pipe, silent)
			)
		
		elif t == 'delete' or t == 'del':
			pipe = PathPipe((read_path(), None))
			
			# Currently has no effects
			overwrite, silent = _parse_action_switchs(args)
			
			actions.append(
				Action(ActionType.Delete, pipe, silent)
			)
		
		elif t == 'ignore':
			ignored_src_files_regex.add(re.compile(args.read()))
		
		elif t == 'project':
			project_path = read_path()
		
		elif t == 'source':
			src_folder = read_path()
			found_src_folder = True
		
		elif t == 'output':
			output_folder = read_path()
			found_out_folder = True
		
		elif t == 'include_file_type':
			include_file_types.add(args.read())
		
		elif t == 'include_default':
			include_file_types += set(get_include_file_types_default(args.read()))
		
		elif len(t) > 7 and t[:7] == 'define:':
			custom_path_defines[t[7:]] = str(read_path())
	
	if not found_src_folder:
		raise ValueError("No 'source' folder path found: A required argument can't be found, refere to the docs!")
	if not found_out_folder:
		raise ValueError("No 'output' folder path found: A required argument can't be found, refere to the docs!")
	
	# if len(include_file_types) == 0:
	# 	# default c++
	# 	include_file_types = set(get_include_file_types_default('c++'))
	include_file_types |= set(get_include_file_types_default('c++'))
	
	return Request(
		_project=project_path,
		_source_folder=src_folder,
		_output_folder=output_folder,
		_ignored_source_files=ignored_src_files_regex,
		_actions=actions,
		_strict=strict,
		_include_file_types=include_file_types,
		_override_include_folder=override_include_folder,
		_custom_path_defines=custom_path_defines
	)

def _is_valid_file(p: str):
	# noinspection PyBroadException
	try:
		p = Path(p).resolve()
		return p.is_file()
	except:...
	return False

def create_new_template_hivefile(filepath: str | Path, override: bool = False):
	if isinstance(filepath, str):
		filepath = Path(filepath)
	filepath = filepath.resolve().absolute()
	if filepath.is_dir():
		filepath = filepath.joinpath('hivec.args')
	
	if filepath.exists():
		if not override:
			return f"Can't create a new hivefile, path '{filepath}' already exists"
	
	with open(filepath, 'w') as f:
		f.writelines(
			i + '\n' for i in (
				'# project path, or \'..\' to make it the current dir the file resides in',
				'project ".."',
				'',
				'# source path, where the headers should be, \'__proj__\' is replaced by the project path.',
				'# the source path replaces every \'__src__\' in the other paths',
				'source "__proj__\src"',
				'',
				'# ouput path, where the headers should go, \'__proj__\' is replaced by the project path',
				'# the output path replaces every \'__out__\' in the other paths',
				'output "__proj__\output"',
				'',
				'# headers with their path matching the given REGEX EXP (note that it does not use glob) are ignored.',
				'# just "pch.h" will ignore every file named "pch.h" or has "pch.h" in it\'s filepath',
				'ignore pch.h',
				'ignore internal.h',
				'',
			)
		)
	print(f"Created a new hivec deploy project file at '{filepath}'")
	return None

def main():
	global async_mode
	live = False
	
	args: Tape[str] = Tape(sys.argv[1:])
	
	if len(args) == 0 or args.peek() == '-h' or args.peek() == '--help' or args.peek() == '?':
		print_general_help()
		input("\nPress anykey to exit...")
		return
	
	first_command = args.peek()
	
	valid_first_command_path: bool = _is_valid_file(first_command)
	
	if valid_first_command_path:
		mode = RunMode.FileArgs
	else:
		args.read()
		match first_command:
			# case '/f':
			# 	mode = RunMode.FileArgs
			case '/c':
				mode = RunMode.CommandLineArgs
			case 'new':
				mode = RunMode.NoMode
				p = os.getcwd()
				
				if args:
					if os.path.isdir(args.peek()):
						p = Path(p).joinpath('hivec.args').resolve()
						args.read()
					elif os.path.isfile(args.peek()):
						p = Path(p).resolve()
						args.read()
					
				
				err = create_new_template_hivefile(p, args and (args.peek() == '/overwrite' or args.peek() == '/o'))
				if err is not None:
					print(err)
			case _:
				mode = RunMode.FileArgs
	
	requests: list[Request] = []
	
	if mode != RunMode.NoMode:
		print("Actvaiting:", mode.name)
	
	if mode == RunMode.FileArgs:
		while args:
			file_path = Path(args.read()).resolve().absolute()
			fargs = Tape(pipin_args(file_path))
			try:
				req = generate_request_from_args(fargs, file_path.parent)
			except:
				print(f"ARGS FILE '{file_path}' DUMP:")
				if not file_path.exists() or not file_path.is_file():
					print("  NO FILE EXISTS DO DUMP")
				else:
					print('  ' + file_path.read_text('utf-8').replace('\n', '\n  '))
				print("\nARGS PARSED:")
				print(fargs.data)
				raise
			requests.append(req)
			req.run()
	elif mode == RunMode.CommandLineArgs:
		req = generate_request_from_args(args, Path(os.getcwd()))
		req.run()
	
	print("[HiveCpp]--------------Done------------")
	
	if live:
		input()

