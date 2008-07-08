
import urllib
import htmlTools

x = urllib.urlopen( "http://www.google.com/" ).read()

for line in htmlTools.getContent( x )[1]:
	print line.encode( "shift-jis", "ignore" )
