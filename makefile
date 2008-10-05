SRC = \
	config.py \
	html2text.py \
	main.py \
	misc.py \
	parallel.py \
	wwwInfo.py


check: $(SRC)
	pychecker $(SRC)

package: $(SRC)
	tar cvzf www-checker.tar.gz $(SRC)

clean:
	-rm *.pyc
