
import re
import BeautifulSoup as _BeautifulSoup


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
		"x-euc-jp": "euc-jp",
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


_BeautifulSoup.UnicodeDammit = MyUnicodeDammit
_BeautifulSoup.CHARSET_RE = re.compile(
	"((^|;)\s*[cC][hH][aA][rR][sS][eE][tT]=)([^;]*)"
)

BeautifulSoup = _BeautifulSoup.BeautifulSoup
