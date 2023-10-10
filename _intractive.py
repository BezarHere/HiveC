# All rights (C) 2023 reserved for Zaher abdolatif abdorab babakr (Bezar/BotatoDev)
"""loaded to process hivec when it's main is invoked"""
import enum
import glassy.utils
import os
import re
import sys
from glassy.utils import Tape
from pathlib import Path

from _hivefile import Action, Request, PathPipe, ActionType
from docs import gen_help

async_mode: bool = False

_verbose: bool = False

class PrettyStr(str):
	
	def __new__(cls, obj) -> str:
		return obj.__pretty_str__()
	

class RunMode(enum.IntEnum):
	NoMode = 0
	FileArgs = 1
	CommandLineArgs = 2
	ReadoutFileArgs = 3
	
	@property
	def name(self):
		return ('no mode', 'args file mode', 'command line args mode', 'readout args file')[int(self)]


def print_help(subject: str):
	if not subject:
		print(gen_help())
		return


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
	
	return False, Fal


def _proc_args_line(line: str):
	line = line.strip()
	if not line and line[0] == '#':
		return ''
	return line.strip('"')


def _is_valid_file(p: str):
	# noinspection PyBroadException
	try:
		p = Path(p).resolve()
		return p.is_file()
	except:
		# TODO: error handling
		...
	return False


def parse_args_file(args_path: Path):
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

def parse_blacklist_regex(t: Tape[str]):
	base = t.read()
	flags: re.RegexFlag = re.UNICODE
	while t:
		match t.peek():
			case '/s' | '/ignorecase':
				flags |= re.IGNORECASE
			case '/S' | '/-ignorecase' | '/-s':
				flags |= ~re.IGNORECASE
			case '/d' | '/dotall':
				flags |= re.DOTALL
			case '/D' | '/-dotall' | '/-d':
				flags |= ~re.DOTALL
			case '/m' | '/multiline':
				flags |= re.MULTILINE
			case '/M' | '/-multiline' | '/-m':
				flags |= ~re.MULTILINE
			case _:
				break
		t.read()
	return re.compile(base, flags)


def generate_request_from_args(args: Tape[str], working_path: Path):
	found_src_folder: bool = False
	found_out_folder: bool = False
	working_path.resolve()
	working_path_str = str(working_path).strip('\\').strip('/')
	
	def read_path():
		s = args.read().strip().strip('"')
		if len(s) >= 2 and s[:2] == '..':
			s = working_path_str + s[2:]
		return Path(s)
	
	project_path: Path = Path()
	src_folder: Path = Path()
	output_folder: Path = Path()
	
	blacklist_files_regex: set[re.Pattern] = set()
	actions: list[Action] = list[Action]()
	custom_path_defines: dict[str, str] = dict[str, str]()
	include_file_types: set[str] = set[str]()
	inverted_blacklist: bool = False
	custom_include_dir: Path | None = None
	
	override_include_folder: bool = True
	strict: bool = False
	
	while args:
		t = args.read()
		
		# paramter
		if t[0] == '-' and t[1] == '-':
			t = t[2:].lower()
			
			if t == "keep-inc" or t == "keep-includes":
				override_include_folder = False
			continue
		
		match t:
		# strict
			case '/S':
				strict = True
		# live
			case '/l':
				live = True
			case 'copy':
				pipe = PathPipe((read_path(), read_path()))
				overwrite, silent = _parse_action_switchs(args)
				
				actions.append(
					Action(ActionType.Copy if overwrite else ActionType.Copy, pipe, silent)
				)
			
			case 'move':
				pipe = PathPipe((read_path(), read_path()))
				overwrite, silent = _parse_action_switchs(args)
				
				actions.append(
					Action(ActionType.Move if overwrite else ActionType.MoveNoOverwrite, pipe, silent)
				)
			
			case 'rename':
				pipe = PathPipe((read_path(), read_path()))
				overwrite, silent = _parse_action_switchs(args)
				
				actions.append(
					Action(ActionType.RenameOverwrite if overwrite else ActionType.Rename, pipe, silent)
				)
			
			case 'delete' | 'del':
				pipe = PathPipe((read_path(), None))
				
				# Currently has no effects
				overwrite, silent = _parse_action_switchs(args)
				
				actions.append(
					Action(ActionType.Delete, pipe, silent)
				)
			
			case 'ignore':
				print("[DEPRICATION] use 'blacklist' instad of 'ignore'")
				blacklist_files_regex.add(parse_blacklist_regex(args))
			
			case 'blacklist':
				inverted_blacklist = False
				blacklist_files_regex.add(parse_blacklist_regex(args))
			
			case 'whitelist':
				inverted_blacklist = True
				blacklist_files_regex.add(parse_blacklist_regex(args))
			
			case 'invert_blacklist':
				inverted_blacklist = not inverted_blacklist
			
			case 'project':
				project_path = read_path()
			
			case 'source':
				src_folder = read_path()
				found_src_folder = True
			
			case 'output':
				output_folder = read_path()
				found_out_folder = True
			
			case 'include_dir':
				custom_include_dir = read_path()
			
			case 'include_file_type':
				include_file_types.add(args.read())
			
			case 'include_default':
				include_file_types += set(get_include_file_types_default(args.read()))
			case _:
				if len(t) > 7 and t[:7] == 'define:':
					custom_path_defines[t[7:]] = str(read_path())
				else:
					print(f"[Warning] Unknown argument: '{t}'")
	
	
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
		_source_files_blacklist_regexes=blacklist_files_regex,
		_inverted_blacklist=inverted_blacklist,
		_actions=actions,
		_strict=strict,
		_include_file_types=include_file_types,
		_override_include_folder=override_include_folder,
		_custom_path_defines=custom_path_defines,
		_custom_include_path=custom_include_dir
	)

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
				'blacklist pch.h',
				'blacklist internal.h',
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
		print(gen_help())
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
			case 'show':
				mode = RunMode.ReadoutFileArgs
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
	
	if mode == RunMode.FileArgs or mode == RunMode.ReadoutFileArgs:
		if not args:
			args = Tape[str]([Path(os.getcwd()).resolve().absolute().joinpath('hivec.args')])
		
		while args:
			file_path = Path(args.read()).resolve().absolute()
			fargs = Tape(parse_args_file(file_path))
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
			if mode == RunMode.ReadoutFileArgs:
				print(PrettyStr(req))
			else:
				req.run()
	elif mode == RunMode.CommandLineArgs:
		req = generate_request_from_args(args, Path(os.getcwd()))
		req.run()
	
	print("[HiveC]--------------Done------------")
	
	if live:
		input()

