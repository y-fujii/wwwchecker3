
import contextlib


@contextlib.contextmanager
def disposing( obj ):
	yield obj
	obj.__del__()
