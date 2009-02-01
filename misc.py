# by y-fujii <fuji at mail-box.jp>, public domain

import contextlib


@contextlib.contextmanager
def disposing( obj ):
	yield obj
	if hasattr( obj, "__del__" ):
		obj.__del__()
