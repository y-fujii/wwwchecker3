# (c) Yasuhiro Fujii <fuji at mail-box dot jp> / 2-clause BSDL

import contextlib


@contextlib.contextmanager
def disposing( obj ):
	yield obj
	obj.__del__()
