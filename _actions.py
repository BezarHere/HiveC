import enum
import glassy.utils
from dataclasses import dataclass
from pathlib import Path

class ActionType(enum.IntEnum):
	Copy = 0
	Move = 1
	Rename = 2
	Delete = 3

@dataclass(slots=True, frozen=True)
class Action:
	action_type: ActionType
	source: Path
	destination: Path
	strict: bool
	
	def execute(self):
		# TODO
		match self.action_type:
			case _:
				...
	

_action_name_type_table: dict[str, ActionType] =\
	{
		"copy": ActionType.Copy,
		"move": ActionType.Move,
		"rename": ActionType.Rename,
		"del": ActionType.Delete,
		"delete": ActionType.Delete,
	}

_action_name_type_table_rev = { j: i for i, j in _action_name_type_table.items() }

def _get_actions_print_list():
	s = ""
	l = len(_action_name_type_table_rev.keys())
	for i, v in enumerate(_action_name_type_table_rev.values()):
		if i == l - 1:
			s += ' or '
		elif i > 0:
			s += ', '
		s += v
	return s

def load_action(data: dict[str]):
	ac_type: ActionType
	source: Path
	destination: Path
	strict = 'strict' in data and data['strict']
	
	if not 'type' in data:
		raise AttributeError("No Type found for the action")
	
	if not isinstance(data['type'], str):
		raise TypeError(f"Action type should be a type string, and can be any of the strings: {_get_actions_print_list()} (case-insenstive)")
	
	ac_type_str = data['type'].lower().strip()
	
	if not ac_type_str in _action_name_type_table.keys():
		raise ValueError(f"Action type should be and ONLY be any of the strings: {_get_actions_print_list()} (case-insenstive)")
	
	ac_type = _action_name_type_table[ac_type_str]
	
	match ac_type:
		case ActionType.Copy | ActionType.Move:
			if not ('from' in data and 'to' in data):
				raise AttributeError("Any move/copy action requires a 'from' field and a 'to' field")
			
			if not isinstance(data['from'], str):
				raise TypeError("the 'from' field in a move/copy action should be a string (path) type")
			
			if not isinstance(data['to'], str):
				raise TypeError("the 'to' field in a move/copy action should be a string (path) type")
			
			
			source = Path(data['from'])
			destination = Path(data['to'])
			
			
		case ActionType.Rename:
			if not ('file' in data or 'folder' in data) or not 'new_name' in data:
				raise AttributeError("Every 'rename' action requires a 'file'/'folder' field and a 'new_name' field")
			if 'file' in data and 'folder' in data:
				raise AttributeError("The 'rename' action requires a 'file' field or a 'folder' field, NOT both!")
			
			raw_source = data['file'] if 'file' in data else data['folder']
			
			if not isinstance(raw_source, str):
				raise TypeError("the 'file'/'folder' fields should be string types and pointing to a valid file/folder")
			
			if not isinstance(data['new_name'], str):
				raise TypeError("the 'new_name' field should be a string type")
			
			if not valid_filename(data['new_name']):
				raise ValueError(f"the 'new_name' field should be a valid filename, not this: \"{data['new_name']}\"")
			
			source = Path(raw_source)
			destination = Path(data['new_name'])
		
		
		case ActionType.Delete:
			if not ('file' in data or 'folder' in data) or not 'new_name' in data:
				raise AttributeError("Every 'delete'/'del' action requires a 'file'/'folder' field")
			if 'file' in data and 'folder' in data:
				raise AttributeError("The 'delete'/'del' action requires a 'file' field or a 'folder' field, NOT both!")
			
			raw_source = data['file'] if 'file' in data else data['folder']
			
			if not isinstance(raw_source, str):
				raise TypeError("the 'file'/'folder' fields should be string types and pointing to a valid file/folder")
			
			source = Path(raw_source)
	
	return Action(ac_type, source, destination, flag)

