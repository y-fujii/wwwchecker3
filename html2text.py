# by y.fujii <y-fujii at mimosa-pudica.net>, public domain

import re
import sgmllib


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
			return unicode( src, enc )
		except UnicodeDecodeError, err:
			if err.end > bestScore:
				bestScore = err.end
				bestEnc = enc

	return unicode( src, bestEnc, "ignore" )


class HTML2TextParser( sgmllib.SGMLParser ):

	tagsBlock = [
		"h1", "h2", "h3", "h4", "h5", "h6",
		"ul", "ol", "li", "dl", "dt", "dd",
		"p", "div", "blockquote", "pre",
		"form", "table", "tr", "td", "br",
		"hr", "address", "fieldset",
		"html", "body", "head", "center",
		"title", "script", "style", # quirks
	]


	def __init__( self ):
		sgmllib.SGMLParser.__init__( self )
		self.buff = ""
		self.text = []
		self.title = ""
	

	def close( self ):
		sgmllib.SGMLParser.close( self )
		line = self.nextLine()
		if line != "":
			self.text.append( line )

	
	def nextLine( self ):
		line = re.sub( "[ \t\r\n]+", " ", self.buff ).strip()
		self.buff = ""
		return line


	def unknown_starttag( self, tag, _ ):
		if tag in self.tagsBlock:
			line = self.nextLine()
			if line != "":
				self.text.append( line )

		if tag in [ "script", "style" ]:
			self.setliteral()
	

	def unknown_endtag( self, tag ):
		if tag in [ "script", "style" ]:
			self.nextLine()
		elif tag == "title":
			self.title = self.nextLine()
		elif tag in self.tagsBlock:
			line = self.nextLine()
			if line != "":
				self.text.append( line )


	def handle_data( self, data ):
		self.buff += data
	

	def convert_charref( self, name ):
		try:
			return unichr( int( name ) )
		except StandardError:
			return None


def html2Text( html ):
	html = unicodeAuto( html )
	html = re.sub( "<([^<>]+)/>", "<\\1 />", html )
	parser = HTML2TextParser()
	parser.feed( html )
	parser.close()
	return (parser.title, parser.text)
