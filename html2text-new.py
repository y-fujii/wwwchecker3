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
		"hr", "address", "fieldset", "body",
		"script", "noscript", "head", "title",
		"style", "center",
	]

	tagsStacked = [
		"div", "ul", "ol", "dl", "table",
		"body", "head", "script", "style",
	]

	tagsIgnore = [
		"script", "style",
	]

	def __init__( self ):
		sgmllib.SGMLParser.__init__( self )
		self.tags = []
		self.buff = ""
		self.text = []
		self.title = ""
	
	
	def nextLine( self ):
		line = re.sub( "[ \t\r\n]+", " ", self.buff ).strip()
		self.buff = ""
		return line


	def unknown_starttag( self, tag, _ ):
		if tag in self.tagsBlock:
			line = self.nextLine()
			if self.tags and ("script" in self.tags or "style" in self.tags):
				pass
			elif line != "":
				self.text += [ line ]

		if tag in [ "script", "style" ]:
			self.setliteral()

		if tag in self.tagsStacked:
			self.tags += [ tag ]
	

	def unknown_endtag( self, tag ):
		if tag in self.tagsBlock:
			line = self.nextLine()
			if tag == "title":
				self.title = line
			if self.tags and ("script" in self.tags or "style" in self.tags):
				pass
			elif tag in [ "script", "style" ]:
				pass
			elif line != "":
				self.text += [ line ]

		if tag in self.tags:
			nextTag = self.tags.pop()
			if nextTag != nextTag():
				pass


	def handle_data( self, data ):
		print self.tags, data.encode( "euc-jp", "ignore" )
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
