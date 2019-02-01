wwwchecker: $(wildcard src/*) makefile
	rm -rf build && \
	cp -r src build && \
	cd build && \
	git clone --depth 1 -b release https://github.com/urllib3/urllib3/ urllib3-git && \
	mv urllib3-git/src/urllib3 . && \
	rm -rf urllib3-git && \
	find . | xargs touch -t 197001010000 && \
	7z a -tzip -mtc=off -mx=9 wwwchecker.pyz * && \
	{ echo '#!/usr/bin/env python3'; cat wwwchecker.pyz; } > ../wwwchecker && \
	chmod 755 ../wwwchecker

.PHONY: clean
clean:
	rm -rf build wwwchecker
