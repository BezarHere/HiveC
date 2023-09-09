from pathlib import Path
import tomllib as toml
from typing import Any, BinaryIO, overload
from functools import cache
from _actions import Action
import re


class HiveFile:
	project: Path
	sources: list[Path]
	outputs: list[Path]
	_source_output_links: dict[int, int]
	actions: list[Action]
	
	def __init__(self, project: Path):
		self.project = project
		_load(self, toml.load(project))
	
	
	
	
	def get_linked_source_output(self):
		d = dict[Path, Path]()
		for i, v in enumerate(self.sources):
			if i in self._source_output_links:
				d[v] = self.outputs[self._source_output_links[i]]
			else:
				d[v] = self.outputs[i]
		return d

	def excute_actions(self):
		for i in self.actions:
			i.execute()
	
# ----------------------------------------


_repr_types_re = re.compile(r"(\w+)[ ,\]]")

@cache
def _repr_types(types):
	s = tuple(_repr_types_re.finditer(str(types) + ' '))
	r = ''
	sl = len(s)
	for i, v in enumerate(s):
		if i == sl - 1:
			r += ' or '
		elif i != 0:
			r += ', '
		r += v
	return r

def _load_typed(name: str, typed: type, data: dict, optional: bool = True):
	if not name in data:
		if optional:
			return None
		raise AttributeError(f"the required field '{name}' does not exist")
	if not isinstance(data[name], typed):
		raise TypeError(f"the field '{name}' should be a type {_repr_types(typed)}")
	return data[name]

def _load_unwrapped(hivefile: HiveFile, data: dict[str, Any]):
	hivefile.sources = []
	hivefile.outputs = []
	
	n = _load_typed('source', str | Path, data)
	if n is not None:
		hivefile.sources.append(Path(n))
	
	if 'sources' in data:
		...


def _load(hivefile: HiveFile, data: dict[str, Any]):
	try:
		_load_unwrapped(hivefile, data)
	except e as BaseException:
		raise RuntimeError(f"Error will loading the hive file at '{hivefile.project}':")
		raise e