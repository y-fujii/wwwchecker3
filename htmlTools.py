
import re
import urllib
import BeautifulSoup


inlineTags = [
	"a", "img", "span", "b", "i", "em", "strong", "q",
]


def toTextList( e ):
	if isinstance( e, BeautifulSoup.NavigableString ):
		if type( e ) in [
			BeautifulSoup.NavigableString,
			BeautifulSoup.CData,
		]:
			if e.string.strip() != "":
				return [ re.sub( "[ \t\n\r]+", " ", e.string ) ]

	elif isinstance( e, BeautifulSoup.Tag ):
		if e.name != "script":
			return sum( [ toTextList( e ) for e in e.contents ], [] )

	return []


def getContent( html ):
	soup = BeautifulSoup.BeautifulSoup(
		html,
		convertEntities = BeautifulSoup.BeautifulSoup.XHTML_ENTITIES,
	)
	title = " ".join( toTextList( soup.find( "title" ) ) )
	body = toTextList( soup.find( "body" ) )

	return (title, body)


if __name__ == "__main__":
	import pprint

	soup = BeautifulSoup.BeautifulSoup(
		#urllib.urlopen( "http://park8.wakwak.com/~attyonnburike/hp/top02.htm"),
		urllib.urlopen( "http://psychodoc.eek.jp/diary/" ),
		convertEntities = BeautifulSoup.BeautifulSoup.XHTML_ENTITIES,
	)
	for line in toTextList( soup.find( "body" ) ):
		print line.encode( "shift-jis", "ignore" )

