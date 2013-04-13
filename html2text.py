# by Yasuhiro Fujii <y-fujii at mimosa-pudica.net>, public domain

import re
import io
import unicodedata
import html.parser
import html.entities


encodings = [
	"iso-2022-jp",
	"utf-8",
	"euc-jp",
	"cp932",
]

def unicodeAuto( src, encs = encodings ):
	bestScore = -1
	bestEnc = None
	for enc in encs:
		try:
			return str( src, enc )
		except UnicodeDecodeError as err:
			if err.end > bestScore:
				bestScore = err.end
				bestEnc = enc

	return str( src, bestEnc, "ignore" )


def normalizeText( text ):
	text = unicodedata.normalize( "NFKC", text )
	text = re.sub( "[ \t\r\n]+", " ", text )
	return text.strip()


class HTML2TextParser( html.parser.HTMLParser ):

	# ref: http://www.w3.org/TR/html5/
	tagsBlock = frozenset( [
		"html", "head", "title", "base", "link", "meta", "style", "script",
		"noscript", "body", "article", "section", "nav", "aside", "h1", "h2",
		"h3", "h4", "h5", "h6", "hgroup", "header", "footer", "address", "p",
		"hr", "pre", "blockquote", "ol", "ul", "li", "dl", "dt", "dd",
		"figure", "figcaption", "div", "table", "caption", "colgroup", "col",
		"tbody", "thead", "tfoot", "tr", "br",
	] )


	def __init__( self ):
		html.parser.HTMLParser.__init__( self )
		self.bufN = io.StringIO()
		self.bufA = io.StringIO()
		self.text = []
		self.title = ""
		self.anchor = False
		self.head   = False
	

	def close( self ):
		html.parser.HTMLParser.close( self )
		self.pushLine()

	
	def nextLine( self ):
		lineN = normalizeText( self.bufN.getvalue() )
		lineA = normalizeText( self.bufA.getvalue() )
		self.bufN = io.StringIO()
		self.bufA = io.StringIO()
		self.anchor = False
		self.head   = False
		return (lineN, lineA)


	def pushLine( self ):
		(lineN, lineA) = self.nextLine()
		if lineN != "":
			self.text.append( (lineN, lineA) )


	def handle_starttag( self, tag, _ ):
		if tag == "a":
			self.anchor = True
		elif re.match( "h[1-6]", tag ):
			self.head = True
		elif tag in self.tagsBlock:
			self.pushLine()
	

	def handle_endtag( self, tag ):
		if tag == "a":
			self.anchor = False
		elif tag == "title":
			(self.title, _) = self.nextLine()
		elif tag in [ "script", "style" ]:
			self.nextLine()
		elif tag in self.tagsBlock:
			self.pushLine()


	def handle_data( self, data ):
		self.bufN.write( data )
		if not self.anchor or self.head:
			self.bufA.write( data )
	

	def handle_entityref( self, name ):
		try:
			c = chr( html.entities.name2codepoint[name] )
		except KeyError:
			c = " %s " % name
		self.handle_data( c )

	def handle_charref( self, name ):
		if name.startswith( "x" ):
			n = int( name[1:], 16 )
		else:
			n = int( name )
		self.handle_data( chr( n ) )


def html2Text( html ):
	parser = HTML2TextParser()
	parser.feed( unicodeAuto( html ) )
	parser.close()
	return (parser.title, parser.text)
