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


class HTML2TextParser( html.parser.HTMLParser ):

	# ref: http://www.w3.org/TR/html5/
	tagsBlock = [
		"html", "head", "title", "base", "link", "meta", "style", "script",
		"noscript", "body", "article", "section", "nav", "aside", "h1", "h2",
		"h3", "h4", "h5", "h6", "hgroup", "header", "footer", "address", "p",
		"hr", "pre", "blockquote", "ol", "ul", "li", "dl", "dt", "dd",
		"figure", "figcaption", "div", "table", "caption", "colgroup", "col",
		"tbody", "thead", "tfoot", "tr", "br",
	]


	def __init__( self ):
		html.parser.HTMLParser.__init__( self )
		self.buf = io.StringIO()
		self.text = []
		self.title = ""
	

	def close( self ):
		html.parser.HTMLParser.close( self )
		self.pushLine()

	
	def nextLine( self ):
		line = self.buf.getvalue()
		line = unicodedata.normalize( "NFKC", line )
		line = re.sub( "[ \t\r\n]+", " ", line )
		line = line.strip()
		self.buf = io.StringIO()
		return line


	def pushLine( self ):
		line = self.nextLine()
		if line != "":
			self.text.append( line )


	def handle_starttag( self, tag, _ ):
		if tag in self.tagsBlock:
			self.pushLine()
	

	def handle_endtag( self, tag ):
		if tag in [ "script", "style" ]:
			self.nextLine()
		elif tag == "title":
			self.title = self.nextLine()
		elif tag in self.tagsBlock:
			self.pushLine()


	def handle_data( self, data ):
		self.buf.write( data )
	

	def handle_entityref( self, name ):
		try:
			c = chr( html.entities.name2codepoint[name] )
		except KeyError:
			c = " %s " % name
		self.buf.write( c )

	def handle_charref( self, name ):
		if name.startswith( "x" ):
			n = int( name[1:], 16 )
		else:
			n = int( name )
		self.buf.write( chr( n ) )


def html2Text( html ):
	parser = HTML2TextParser()
	parser.feed( unicodeAuto( html ) )
	parser.close()
	return (parser.title, parser.text)
