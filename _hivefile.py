"""
All rights (C) 2023 reserved for Zaher abdolatif abdorab babakr (Bezar/BotatoDev)
"""
import enum
import io
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
_verbose: bool = True

def query_run_define():
    global _run_define
    if _run_define is not None:
        return
    _run_define = _run

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
                overwritten_file: bool = to_path.exists()
                
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
                print(f"copied '{from_path}' --> '{to_path}'{ ' (overwriten)' if overwritten_file else '' }")
                
            # Move/MoveNoOverwrite
            case ActionType.Move | ActionType.MoveNoOverwrite:
                from_path, to_path = _unravel_pipe(self.data, path_processor)
                overwritten_file: bool = to_path.exists()
                
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
                print(f"moved '{from_path}' --> '{to_path}'{' (overwriten)' if overwritten_file else ''}")
                
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
                print(f"deleted '{target_path}'")
                
            # Rename/RenameOverwrite
            case ActionType.Rename | ActionType.RenameOverwrite:
                from_path, to_path = _unravel_pipe(self.data, path_processor)
                
                
                if not from_path.exists():
                    if self.quite:
                        return
                    raise FileNotFoundError(f"Rename action's source: '{from_path}'")
                

                new_name = Path(str(from_path.parent.absolute()) + '\\' + str(to_path))
                overwritten_file: bool = new_name.exists()
                
                if self.action_type == ActionType.Rename and new_name.exists():
                    if self.quite:
                        return
                    raise NameError(f"There is already a file/folder with the path {new_name}")
                
                # FIXME: Is there a better way?
                shutil.move(from_path, new_name)
                
                print(f"renamed '{from_path}' --> '{to_path}'{' (overwriten)' if overwritten_file else ''}")
                
            # DEFAULT
            case _:
                raise IndexError(f"Invalid/Unknown Action type: {self.action_type}")
                
            
    
    
@dataclass(slots=True, kw_only=True)
class Request:
    _project: Path
    _source_folder: Path
    _output_folder: Path
    
    _source_files_blacklist_regexes: set[re.Pattern] = set[re.Pattern]
    _inverted_blacklist: bool = False
    
    _actions: list[Action]
    
    _strict: bool = False
    
    _include_file_types: set[str]
    _override_include_folder: bool = True  # will delete include folder to apply all changes in src folder to include folder
    
    _custom_path_defines: dict[str, str]
    
    _custom_include_path: Path | str | None = None
    
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
        if self._custom_include_path is None:
            return Path((self.process_path(str(self._output_folder) + '//include')))
        return Path(self.process_path(self._custom_include_path))
    
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
    def blacklist_regexes(self):
        return self._source_files_blacklist_regexes
    
    @property
    def actions(self):
        return self._actions
    
    @property
    def is_blacklist_inverted(self):
        return self._inverted_blacklist
    
    def get_include_file_regex(self):
        return re.compile(f".+?\.({'|'.join(self._include_file_types)})")
    
    
    @cache
    def _replace_builtin(self, s: str):
        if not isinstance(s, str):
            s = str(s)
        return s.replace('__proj__', str(self._project)).replace('__src__', str(self._source_folder)).replace("__out__", str(self._output_folder))
    
    
    def process_path(self, s: str):
        # puting this before and after the defines helps to evade all overwrites (e.g. --define:proj "Some random, buggy path; not the --proj path!!!")
        s = self._replace_builtin(s)
        
        for i, j in self._custom_path_defines.items():
            s = s.replace(f"__{i}__", j)
        
        s = self._replace_builtin(s)
        return s
    
    def __pretty_str__(self):
        BACKSLASH = '\\'
        
        s = io.StringIO()
        s.write(f'Project path: "{self.project_path}"\n')
        s.write(f'Source dir:   "{self.source_folder}"\n')
        s.write(f'Output dir:   "{self.output_folder}"\n')
        s.write(f'Include dir:  "{self.include_folder}"')
        if self._custom_include_path is not None:
            s.write(' (custom)\n')
        else:
            s.write(' (default)\n')
        
        s.write(f'STRICT FLAG {"ENABLED" if self.is_strict else "DISABLED"}\n')
        
        if self.blacklist_regexes:
            if self.is_blacklist_inverted:
                s.write(f'Whitelist (Regex):\n')
            else:
                s.write(f'Blacklist (Regex):\n')
            
            brlen = len(self.blacklist_regexes)
            
            for i, v in enumerate(self.blacklist_regexes):
                s.write(f'{ (BACKSLASH if i == brlen - 1 else "+") }---"{v.pattern}"\n')
        else:
            if self.is_blacklist_inverted:
                s.write(f'No whitelist present\n')
            else:
                s.write(f'No blacklist present\n')
        
        if self._custom_path_defines:
            s.write("Definitions:\n")
            brlen = len(self._custom_path_defines)
            for k in self._custom_path_defines:
                s.write(f'  defined "{k}" as "{self.process_path(self._custom_path_defines[k])}"\n')
        else:
            s.write("No defines present\n")
        
        if self.actions:
            s.write("Actions:\n")
            brlen = len(self.actions)
            for i, v in enumerate(self.actions):
                s.write(f'{(BACKSLASH if i == brlen - 1 else "+")}---{v.name}')
                s.write(f' "{self.process_path(v.data[0])}"')
                if v.data[1] is not None:
                     s.write(f' "{self.process_path(v.data[1])}"\n')
                else:
                    s.write(f'\n')
        else:
            s.write("No actions present\n")
        return s.getvalue()
        
        
        
    
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
    
    if not src_path.exists():
        raise ValueError(f"src path DOESN'T exsit: '{src_path}'")
    if not src_path.is_dir():
        raise ValueError(f"src path is NOT a directory: '{src_path}'")
    
    print(f"started deploying project '{rq.project_path}'")
    print(f"project included directory: '{rq.include_folder}'")
    print(f"project source directory: '{rq.source_folder}'")
    print(f"project output directory: '{rq.output_folder}'")
    
    if rq.wipe_include_destination_on_build:
        if include_path.exists():
            shutil.rmtree(include_path)
            if _verbose:
                print(f"cleared include path '{include_path}'")
        os.makedirs(include_path, exist_ok=True)
    elif not include_path.is_dir() or not include_path.exists():
        if rq.is_strict:
            raise ValueError(f"[STRICT] invalid include path '{include_path}'")
        os.makedirs(include_path, exist_ok=True)
    
    include_files = rq.get_source_file()
    
    blacklist_regexes = rq.blacklist_regexes
    
    for ppath in include_files:
        if any((i.search(str(ppath.absolute())) is not None or i.search(str(ppath.name)) is not None) for i in blacklist_regexes):
            if not rq.is_blacklist_inverted:
                continue
        elif rq.is_blacklist_inverted:
            continue
        os.makedirs(ppath.parent, exist_ok=True)
        
        ppath_target = Path(str(ppath.absolute()).replace(str(src_path.absolute()), str(include_path.absolute()) + '\\')).resolve()
        shutil.copy(ppath, ppath_target)
        
        if _verbose:
            print(f"deployed header '{ppath}'\t-->\t'{ppath_target}'")

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
query_run_define()

