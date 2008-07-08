
import re
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
BeautifulSoup.CHARSET_RE = re.compile(
	"((^|;)\s*[cC][hH][aA][rR][sS][eE][tT]=)([^;]*)"
)



def stripTags( soup, e, leftTags ):
	if isinstance( e, BeautifulSoup.Tag ):
		strippedChildren = sum( [ stripTags( soup, c, leftTags ) for c in e.contents ], [] )
		if e.name in leftTags:
			dst = BeautifulSoup.Tag( soup, e.name, e.attrs ) #, e.parent, e.previous )
			for c in strippedChildren:
				dst.append( c )
			return [ dst ]
		else:
			return strippedChildren
	else:
		return [ e ]


def joinString( soup, e ):


def flatten( soup, e ):
	#if isinstance( e, BeautifulSoup.NavigableString ):
	if type( e ) in [
		BeautifulSoup.NavigableString,
		BeautifulSoup.CData,
	] and e.string.strip() != "":
		return [ re.sub( "[ \t\n\r]+", " ", e.string ) ]

	elif isinstance( e, BeautifulSoup.Tag ) and e.name != "script":
		return sum( [ flatten( soup, e ) for e in e.contents ], [] )
	
	else:
		return []


def getContent( html ):
	blockTags = [
		"p", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "dir", "menu",
		"pre", "dl", "div", "center", "noscript", "noframes", "blockquote",
		"form", "isindex", "hr", "table", "fieldset", "address", "multicol",
	]

	soup = BeautifulSoup.BeautifulSoup(
		html,
		convertEntities = BeautifulSoup.BeautifulSoup.XHTML_ENTITIES,
	)

	body = soup.find( "body" )
	print body.prettify()
	body = stripTags( soup, body, blockTags )
	print body[0].prettify()
	body = flatten( soup, body[0] )

	title = soup.find( "title" )
	title = " ".join( flatten( soup, title ) )

	return (title, body)
