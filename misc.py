# by y-fujii <fuji at mail-box.jp>, public domain

import contextlib


@contextlib.contextmanager
def disposing( obj ):
	yield obj
	obj.__del__()
