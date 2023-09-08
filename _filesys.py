from typing import BinaryIO
from pathlib import Path

def get_hash(f: BinaryIO):
	return hash(bytes(f.read()))

def copy_no_overwrite(src: Path, dst: Path):
	...
