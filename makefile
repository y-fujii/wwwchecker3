SRC = \
	config.py \
	html2text.py \
	main.py \
	misc.py \
	parallel.py \
	wwwInfo.py


check: $(SRC)
	pyflakes $(SRC)

package: $(SRC)
	tar cvzf wwwChecker.tar.gz $(SRC)

clean:
	rm -f *.pyc wwwChecker.tar.gz
