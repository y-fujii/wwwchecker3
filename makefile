SRC = \
	parallel.py \
	html2text.py \
	wwwInfo.py \
	__main__.py \
	config.py

check: $(SRC)
	pyflakes $(SRC)

package: $(SRC)
	cd ..; \
	tar cvzf wwwChecker.tar.gz $(addprefix wwwChecker/, $(SRC))

clean:
	rm -f *.pyc
