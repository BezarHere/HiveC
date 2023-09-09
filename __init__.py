
__version__ = '0.1.0'

import typing
from _hivefile import HiveFile

def main():
	x = int | float
	y = typing.Union[int, float]
	print(str(x), str(y))
	print(repr(x), repr(y))

if __name__ == '__main__':
	main()

del main