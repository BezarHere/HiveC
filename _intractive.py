"""
All rights (C) 2023 reserved for Zaher abdolatif abdorab babakr (Bezar/BotatoDev)
"""
import asyncio

import glassy.utils
import re
import sys
from glassy.utils import Tape
from pathlib import Path

from ._hivefile import Request, Action, ActionType, PathPipe

async_mode: bool = False
files_mode: bool = False

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
	
	show("[REQUIRED] source <source path>")
	level += 1
	show("Where is the source code (headers)?")
	show("The folder where all the headers will be loaded.")
	show("The source path replaces every '__src__' in other paths.")
	
	print()
	
	level -= 1
	show("[REQUIRED] source_output <source output path>")
	level += 1
	show("Where should the headers go after build?")
	show("The folder where all the headers will be put to be loaded with the library.")
	show("The include path replaces every '__inc__' in other paths.")
	
	print()
	
	level -= 1
	show("[REQUIRED] project <project path>")
	level += 1
	show("Where is the project?")
	show("The project path replaces every '__proj__' in other paths.")
	
	print()
	
	level -= 1
	show("copy <src path> <dst path>")
	level += 1
	show("A copy command from the src path to the dst path.")
	show("Add the switch '/o' to make it overwrite the destination")
	
	print()
	
	level -= 1
	show("move <src path> <dst path>")
	level += 1
	show("A move command from the src path to the dst path.")
	show("Add the switch '/o' to make it overwrite the destination")
	
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
	
	print()
	
	level -= 1
	show("/f <args file path>")
	level += 1
	show("Runs the argument file, no more argument from the commandline will be read if this switch is present")
	
	print()
	
	level -= 1
	show("/s")
	level += 1
	show("Directs the input from the commandline arguments, works the same even if removed")


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

def generate_request_from_args(args: Tape[str]):
	found_src_folder: bool = False
	found_inc_folder: bool = False
	
	project_path: Path = Path()
	src_folder: Path = Path()
	include_folder: Path = Path()
	
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
			pipe = PathPipe(args.read(), args.read())
			t = ActionType.CopyNoOverwrite
			if args.peek() == '/o':
				args.read()
				t = ActionType.Copy
				
			actions.append(Action(t, pipe))
		
		elif t == 'move':
			pipe = PathPipe(args.read(), args.read())
			t = ActionType.MoveNoOverwrite
			if args.peek() == '/o':
				args.read()
				t = ActionType.Move
				
			actions.append(Action(t, pipe))
		
		elif t == 'ignore':
			ignored_src_files_regex.add(re.compile(args.read()))
		
		elif t == 'project':
			project_path = Path(args.read())
		
		elif t == 'source':
			src_folder = Path(args.read())
			found_src_folder = True
		
		elif t == 'source_output':
			include_folder = Path(args.read())
			found_inc_folder = True
		
		elif t == 'include_file_type':
			include_file_types.add(args.read())
		
		elif t == 'include_default':
			include_file_types += set(get_include_file_types_default(args.read()))
		
		elif len(t) > 7 and t[:7] == 'define:':
			custom_path_defines[t[7:]] = args.read()
	
	if not found_src_folder:
		raise ValueError("No src folder path found: A required argument can't be found, refere to the docs!")
	if not found_inc_folder:
		raise ValueError("No include folder path found: A required argument can't be found, refere to the docs!")
	
	# if len(include_file_types) == 0:
	# 	# default c++
	# 	include_file_types = set(get_include_file_types_default('c++'))
	include_file_types += set(get_include_file_types_default('c++'))
	
	return Request(
		_project=project_path,
		_source_folder=src_folder,
		_include_folder=include_folder,
		_ignored_source_files=ignored_src_files_regex,
		_include_output_folder=include_folder,
		_actions=actions,
		_strict=strict,
		_include_file_types=include_file_types,
		_override_include_folder=override_include_folder,
		_custom_path_defines=custom_path_defines
	)

def _main():
	global files_mode, async_mode
	live = False
	
	args: Tape[str] = Tape(sys.argv[1:])
	
	if len(args) == 0 or args.peek() == '-h' or args.peek() == '--help' or args.peek() == '?':
		print_general_help()
		input("\nPress anykey to exit...")
		exit()
	
	mode_str = args.peek()
	
	if mode_str == '/f':
		args.read()
		files_mode = True
	else:
		if mode_str == '/c':
			args.read()
		elif mode_str == '/l':
			args.read()
			live = True
	
	
	requests: list[Request] = []
	
	if files_mode:
		while args:
			args = Tape(pipin_args(Path(args.read()).resolve()))
			req = generate_request_from_args(args)
			requests.append(req)
			req.run()
			
	else:
		req = generate_request_from_args(args)
		req.run()
	
	print("-------DONE-------")
	
	if live:
		input()
	
	exit(0)


