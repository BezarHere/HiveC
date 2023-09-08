from pathlib import Path
import tomllib
from typing import Any, BinaryIO, overload
import glassy



class HiveFile:
	project: Path
	sources: list[Path]
	outputs: list[Path]
	_source_output_links: dict[int, int]
	
	@overload
	def __init__(self, data: dict[str, Any]):
		proj_sec = data.get("meta")
		if proj_sec is None:
			raise AttributeError("No 'meta' section found in hive.toml")
	
	@overload
	def __init__(self, toml: BinaryIO):
		self.__init__(tomllib.load(toml))
	
	def __init__(self, *args, **kwargs):
		raise NotImplemented()
	
	def get_linked_source_output(self):
		d = dict[Path, Path]()
		for i, v in enumerate(self.sources):
			if i in self._source_output_links:
				d[v] = self.outputs[self._source_output_links[i]]
			else:
				d[v] = self.outputs[i]
		return d



