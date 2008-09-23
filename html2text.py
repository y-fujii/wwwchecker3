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


	def __init__( self ):
		sgmllib.SGMLParser.__init__( self )
		self.buff = u""
		self.text = []
		self.title = ""
	
	
	def normText( self, text ):
		return re.sub( "[ \t\r\n]+", " ", text ).strip()


	def unknown_starttag( self, tag, _ ):
		if tag in self.tagsBlock:
			line = self.normText( self.buff )
			if line != "":
				self.text += [ line ]
			self.buff = u""
	

	def unknown_endtag( self, tag ):
		if tag in self.tagsBlock:
			line = self.normText( self.buff )
			if tag == "title":
				self.title = line
			elif tag in ["script", "style"]:
				pass
			elif line != "":
				self.text += [ line ]

			self.buff = u""


	def handle_data( self, data ):
		self.buff += data
	

	def handle_charref( self, ref ):
		try:
			c = unichr( int( ref ) )
			self.handle_data( c )
		except:
			pass


def html2Text( html ):
	parser = HTML2TextParser()
	parser.feed( unicodeAuto( html ) )
	parser.close()
	return (parser.title, parser.text)
