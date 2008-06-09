
import re
import urllib
import BeautifulSoup


class MyUnicodeDammit( object ):
	encodings = [
		"utf-8",
		"euc-jp",
		"cp932",
		"iso-2022-jp",
	]

	replaceMap = {
		"shift-jis": "cp932",
		"shiftjis": "cp932",
		"sjis": "cp932",
		"x-sjis": "cp932",
	}


	def __init__( self, src, encs, *args, **kws ):
		def f( e ):
			e = e.lower().replace( "_", "-" )
			return self.replaceMap.get( e, e )
		encs = set( f( e ) for e in encs if e != None )

		if len( encs ) > 0:
			(self.unicode, self.originalEncoding) = \
				self.encode( src, encs )
		else:
			(self.unicode, self.originalEncoding) = \
				self.encode( src, self.encodings )


	def encode( self, src, encs ):
		bestScore = -1
		bestEnc = None
		for enc in encs:
			try:
				dst = unicode( src, enc )
			except UnicodeDecodeError, err:
				if err.end > bestScore:
					bestScore = err.end
					bestEnc = enc
			else:
				return (dst, enc)

		return (
			unicode( src, bestEnc, "ignore" ),
			bestEnc,
		)


BeautifulSoup.UnicodeDammit = MyUnicodeDammit


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

