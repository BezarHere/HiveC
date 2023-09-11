"""
All rights (C) 2023 reserved for Zaher abdolatif abdorab babakr (Bezar/BotatoDev)
"""
import enum
from dataclasses import dataclass
from functools import cache
from typing import Callable, Union
import shutil
import os, re
from pathlib import Path

PathPipe = tuple[Path, Path | None]
StrProcessor = Callable[[str], str]

_run_define: Union[Callable, None] = None

_path_split_re = re.compile(r'[\\/]')

class ActionType(enum.IntEnum):
	Copy = 0
	CopyNoOverwrite = 1
	Move = 2
	MoveNoOverwrite = 3
	Delete = 4
	Rename = 5
	RenameOverwrite = 6

_actions_expected_paths_count: dict[ActionType, int] = \
	{
		ActionType.Copy: 2,
		ActionType.CopyNoOverwrite: 2,
		ActionType.Move: 2,
		ActionType.MoveNoOverwrite: 2,
		ActionType.Delete: 1,
		ActionType.Rename: 2,
		ActionType.RenameOverwrite: 2,
	}

_actions_names: dict[ActionType, str] = \
	{
		ActionType.Copy: "copy",
		ActionType.CopyNoOverwrite: "copy (no overwrite)",
		ActionType.Move: "move",
		ActionType.MoveNoOverwrite: "move (no overwrite)",
		ActionType.Delete: "delete",
		ActionType.Rename: "rename",
		ActionType.RenameOverwrite: "rename (overwrite)",
	}


def _unravel_path(p: Path, processor: StrProcessor):
	return Path(processor(str(p.expanduser()))).absolute()
def _unravel_pipe(p: PathPipe, processor: StrProcessor):
	return _unravel_path(Path(p[0]), processor), _unravel_path(Path(p[1]), processor)

# For more custmizablity

errout: Callable = print

def _dumy_str_proc(x: str):
	return x

@dataclass(slots=True, frozen=True)
class Action:
	action_type: ActionType
	data: PathPipe
	quite: bool = False
	
	@property
	def expectes_output(self):
		return _actions_expected_paths_count[self.action_type] > 1
	
	@property
	def name(self):
		return _actions_names[self.action_type]
	
	def execute(self, path_processor: StrProcessor, strict: bool = False):
		match self.action_type:
			# Copy/CopyNoOverwrite
			case ActionType.Copy | ActionType.CopyNoOverwrite:
				from_path, to_path = _unravel_pipe(self.data, path_processor)
				
				if not from_path.exists():
					if self.quite:
						return
					raise FileNotFoundError(f"Copy action's copy source: '{from_path}'")
				
				if not to_path.parent.exists():
					if strict:
						raise ValueError(f"Copy action's copy destination is't valid: '{to_path}'")
					os.makedirs(to_path.parent)
				
				if self.action_type == ActionType.CopyNoOverwrite and to_path.exists():
					return
				
				shutil.copy(from_path, to_path)
				
			# Move/MoveNoOverwrite
			case ActionType.Move | ActionType.MoveNoOverwrite:
				from_path, to_path = _unravel_pipe(self.data, path_processor)
				
				if not from_path.exists():
					if self.quite:
						return
					raise FileNotFoundError(f"Move action's copy source: '{from_path}'")
				
				if not to_path.parent.exists():
					if strict:
						raise ValueError(f"Move action's copy destination is't valid: '{to_path}'")
					os.makedirs(to_path.parent)
				
				if self.action_type == ActionType.MoveNoOverwrite and to_path.exists():
					return
				
				shutil.move(from_path, to_path)
				
			# Delete
			case ActionType.Delete:
				target_path = _unravel_path(self.data[0], path_processor)
				
				if not target_path.exists():
					if strict:
						raise FileNotFoundError(f"Delete action's target: '{target_path}'")
				
				if target_path.is_dir():
					shutil.rmtree(target_path)
				else:
					os.remove(target_path)
				
			# Rename/RenameOverwrite
			case ActionType.Rename | ActionType.RenameOverwrite:
				from_path, to_path = _unravel_pipe(self.data, path_processor)
				
				
				if not from_path.exists():
					if self.quite:
						return
					raise FileNotFoundError(f"Rename action's source: '{from_path}'")
				

				new_name = Path(str(from_path.parent.absolute()) + '\\' + str(to_path))
				
				if self.action_type == ActionType.Rename and new_name.exists():
					if self.quite:
						return
					raise NameError(f"There is already a file/folder with the path {new_name}")
				
				# FIXME: Is there a better way?
				shutil.move(from_path, new_name)
				
			# DEFAULT
			case _:
				raise IndexError(f"Invalid/Unknown Action type: {self.action_type}")
				
			
	
	
@dataclass(slots=True, kw_only=True)
class Request:
	_project: Path
	_source_folder: Path
	_output_folder: Path
	
	_ignored_source_files: set[re.Pattern] = set[re.Pattern]
	
	_actions: list[Action]
	
	_strict: bool = False
	
	_include_file_types: set[str]
	_override_include_folder: bool = True  # will delete include folder to apply all changes in src folder to include folder
	
	_custom_path_defines: dict[str, str]
	
	def __hash__(self):
		return hash((hash(self._project), hash(repr(self)), hash(self._source_folder), hash(self._output_folder)))
	
	@property
	def project_path(self):
		return Path(self.process_path(str(self._project)))
	
	@property
	def source_folder(self):
		return Path(self.process_path(str(self._source_folder)))
	
	@property
	def output_folder(self):
		return Path(self.process_path(str(self._output_folder)))
	
	@property
	def include_folder(self):
		return Path(self.process_path(str(self._output_folder) + '//include'))
	
	@property
	def lib_folder(self):
		return Path(self.process_path(str(self._output_folder) + '//lib'))
	
	@property
	def bin_folder(self):
		return Path(self.process_path(str(self._output_folder) + '//bin'))
	
	@property
	def wipe_include_destination_on_build(self):
		return self._override_include_folder
	
	@property
	def is_strict(self):
		return self._strict
	
	@property
	def ignored_source_files_reqex(self):
		return self._ignored_source_files
	
	@property
	def actions(self):
		return self._actions
	
	def get_include_file_regex(self):
		return re.compile(f".+?\.({'|'.join(self._include_file_types)})")
	
	
	@cache
	def _replace_builtin(self, s: str):
		return s.replace('__proj__', str(self._project)).replace('__src__', str(self._source_folder)).replace("__out__", str(self._output_folder))
	
	
	def process_path(self, s: str):
		# puting this before and after the defines helps to evade all overwrites (e.g. --define:proj "Some random, buggy path; not the --proj path!!!")
		s = self._replace_builtin(s)
		
		for i, j in self._custom_path_defines.items():
			s = s.replace(f"__{i}__", j)
		
		s = self._replace_builtin(s)
		return s
	
	def get_source_file(self):
		skip_re = self.get_include_file_regex()
		def safe_scan(path):
			return (i for i in os.scandir(path) if i.is_dir() or skip_re.search(i.path) is not None)
		search_stack: list[os.DirEntry] = list(safe_scan(self.source_folder))
		files_stack: list[Path] = []
		while search_stack:
			j = search_stack.pop()
			if j.is_dir():
				search_stack += list(safe_scan(j.path))
			else:
				files_stack.append(Path(j.path))
		return files_stack
	
	def run(self):
		_run_define(self)
	

def command_line_path():
	return os.getcwd()


def _process_sources(rq: Request):
	src_path = rq.source_folder
	include_path = rq.include_folder
	filetype_re = rq.get_include_file_regex()
	
	if not src_path.exists():
		raise ValueError(f"src path is DOESN'T exsit: '{src_path}'")
	if not src_path.is_dir():
		raise ValueError(f"src path is NOT a directory: '{src_path}'")
	
	if rq.wipe_include_destination_on_build:
		if include_path.exists():
			shutil.rmtree(include_path)
		os.makedirs(include_path, exist_ok=True)
	elif not include_path.is_dir():
		if rq.is_strict:
			raise ValueError(f"[STRICT] invalid include path '{include_path}'")
		os.makedirs(include_path, exist_ok=True)
	
	include_files = rq.get_source_file()
	
	ignored_source_files_regex = rq.ignored_source_files_reqex
	
	for ppath in include_files:
		if any((i.search(str(ppath.absolute())) is not None or i.search(str(ppath.name)) is not None) for i in ignored_source_files_regex):
			continue
		os.makedirs(ppath.parent, exist_ok=True)
		
		# FIXME: wtf? does it even work?
		shutil.copy(ppath,  Path(str(ppath.absolute()).replace(str(src_path.absolute()), str(include_path.absolute()) + '\\')).resolve())

def _run(req: Request):
	try:
		_process_sources(req)
	except Exception as e:
		print(f"[HIVEFILE]Failing to build at '{req.project_path}'")
		raise e
	
	for i in req.actions:
		try:
			i.execute(req.process_path, req.is_strict)
		except Exception as e:
			print(f"[HIVEFILE]Error while tring to run a {i.name} action:")
			print(f"  with paths: '{i.data[0]}',\n"
				  f"              '{i.data[1]}'")
			print('\t' + repr(e).replace('\n', '\n\t'))
				
	

## Importent!
_run_define = _run
