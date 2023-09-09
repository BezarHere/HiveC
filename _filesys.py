import os.path
from typing import BinaryIO
from pathlib import Path
import shutil

def get_hash(f: BinaryIO):
	return hash(bytes(f.read()))

def copy_no_overwrite(src: Path, dst: Path):
	if not src.exists():
		return False
	if dst.exists():
		src_size = os.path.getsize(src)
		dst_size = os.path.getsize(dst)
		
		if src_size != dst_size:
			shutil.copyfile(src, dst)
			return True
		
		if open(src, 'rb').read() == open(dst, 'rb').read():
			return False
		
	shutil.copyfile(src, dst)
	return True


