
import re
import BeautifulSoup


class CustomDammit( object ):
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
		self.declaredHTMLEncoding = None

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


BeautifulSoup.UnicodeDammit = CustomDammit
BeautifulSoup.BeautifulSoup.start_meta = lambda *args, **kws: None

blockTags = (
	[ "h1", "h2", "h3", "h4", "h5", "h6", "br", "hr" ] +
	BeautifulSoup.BeautifulSoup.NESTABLE_BLOCK_TAGS +
	BeautifulSoup.BeautifulSoup.NESTABLE_LIST_TAGS.keys() +
	BeautifulSoup.BeautifulSoup.NESTABLE_TABLE_TAGS.keys() +
	BeautifulSoup.BeautifulSoup.NON_NESTABLE_BLOCK_TAGS
)


def dumpText( e ):
	if isinstance( e, BeautifulSoup.Tag ):
		buff = ""
		text = []
		for c in e.contents:
			cText = dumpText( c )
			if isinstance( c, BeautifulSoup.Tag ):
				if c.name in blockTags:
					text += cText
					buff = ""
				else:
					l = len( cText )
					if l == 0:
						pass
					elif l == 1:
						buff += cText[0]
					else:
						text += [ buff + cText[0] ]
						buff = cText[-1]
			elif isinstance( c, BeautifulSoup.NavigableString ):
				buff += c.string

		if buff.strip() != "":
			text += [ buff ]
		return text

	elif isinstance( e, BeautifulSoup.NavigableString ):
		return [ e.string ]

	else:
		return []


def getContent( html ):
	soup = BeautifulSoup.BeautifulSoup(
		html,
		convertEntities = BeautifulSoup.BeautifulSoup.XHTML_ENTITIES,
	)

	body = dumpText( soup.find( "body" ) )
	title = " ".join( dumpText( soup.find( "title" ) ) )

	return (title, body)
