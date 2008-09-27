
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
BeautifulSoup.CHARSET_RE = re.compile(
	"((^|;)\s*[cC][hH][aA][rR][sS][eE][tT]=)([^;]*)"
)

blockTags = (
	[ "h1", "h2", "h3", "h4", "h5", "h6", "br", "hr" ] +
	BeautifulSoup.BeautifulSoup.NESTABLE_BLOCK_TAGS +
	BeautifulSoup.BeautifulSoup.NESTABLE_LIST_TAGS.keys() +
	BeautifulSoup.BeautifulSoup.NESTABLE_TABLE_TAGS.keys() +
	BeautifulSoup.BeautifulSoup.NON_NESTABLE_BLOCK_TAGS
)


def tagStrip( soup, src, cond ):
	if isinstance( src, BeautifulSoup.Tag ):
		childr = sum( [ tagStrip( soup, e, cond ) for e in src.contents ], [] )
		if cond( src ):
			return childr
		else:
			dst = BeautifulSoup.Tag( soup, src.name, src.attrs )
			for e in childr:
				dst.append( e )
			return [ dst ]
	else:
		return [ src ]


def tagFilter( soup, src, cond ):
	if isinstance( src, BeautifulSoup.Tag ):
		dst = BeautifulSoup.Tag( soup, src.name, src.attrs )
		print "!", src.contents
		for e in src.contents:
			#if cond( e ):
			#dst.append( tagFilter( soup, e, cond ) )
			dst.append( e )
		print "#", dst.contents
		return dst
	else:
		return src


def tagFlatten( soup, src ):
	if isinstance( src, BeautifulSoup.Tag ):
		return sum( [ tagFlatten( soup, e ) for e in src.contents ], [] )
	else:
		return [ src.string ]


def tagNormalize( e ):
	prevStr = ""




def getContent( html ):
	soup = BeautifulSoup.BeautifulSoup(
		html,
		convertEntities = BeautifulSoup.BeautifulSoup.XHTML_ENTITIES,
	)

	body = soup.find( "body" )
	body = tagFilter( BeautifulSoup.BeautifulSoup(), body, lambda e: True )
	#, lambda e:
	#	type( e ) in [ BeautifulSoup.NavigableString, BeautifulSoup.CData ] or
	#	isinstance( e, BeautifulSoup.Tag ) and e.name != "script"
	#)
	body = tagStrip( soup, body, lambda e: e.name in blockTags )[0]
	body = tagFlatten( soup, body )

	title = soup.find( "title" )
	title = " ".join( tagFlatten( soup, title ) )

	return (title, body)
