# (c) Yasuhiro Fujii <fuji at mail-box dot jp> / 2-clause BSDL

from __future__ import with_statement
import contextlib
import socket
import urllib2
from email import Utils
import time
import difflib
import sgmllib
import html2text


def checkUpdate( old, new ):
	opcodes = difflib.SequenceMatcher( None, old, new ).get_opcodes()

	#nIns = sum(j2 - j1 for (tag, i1, i2, j1, j2) in opcodes if tag != "equal")
	#nDel = sum(i2 - i1 for (tag, i1, i2, j1, j2) in opcodes if tag != "equal")
	#nRep = sum(i2 - i1 + j2 - j1 for (tag, i1, i2, j1, j2) in opcodes if tag == "replace")
	nIns = 0
	nDel = 0
	nRep = 0
	insText = []
	for (tag, i1, i2, j1, j2) in opcodes:
		li = i2 - i1
		lj = j2 - j1
		if tag == "delete":
			nDel += li
		elif tag == "insert":
			nIns += lj
			insText += new[j1:j2]
		elif tag == "replace":
			if li == lj:
				nRep += li
			else:
				nDel += li
				nIns += lj
				insText += new[j1:j2]

	return (
		max( nIns, nDel ),
		insText,
		"-%03d +%03d !%03d" % (nDel, nIns, nRep),
	)


class URLInfo( object ):

	def __init__( self, url ):
		self.url = url
		self.text = []
		self.date = 0
		self.size = 0
		self.ratio = 0
		self.info = ""
		self.diff = []
		self.title = url


	def update(
		self,
		checkUpdate = checkUpdate,
		html2Text = html2text.html2Text,
	):
		req = urllib2.Request( self.url, headers = {
			"if-modified-since": Utils.formatdate( self.date )
		} )
		try:
			f = urllib2.urlopen( req )
		except urllib2.HTTPError, err:
			if err.code == 304:
				self.info = "If-modified-since"
				self.ratio = 0
				return False
			else:
				raise

		with contextlib.closing( f ):
			if "last-modified" in f.info():
				date = Utils.mktime_tz(
					Utils.parsedate_tz( f.info()["last-modified"] )
				)
				if date == self.date:
					self.info = "Last-modified"
					self.ratio = 0
					return False
			else:
				date = time.time()

			if "content-length" in f.info():
				size = f.info()["content-length"]
				if size == self.size:
					self.info = "Content-length"
					self.ratio = 0
					return False
				else:
					self.size = size

			(self.title, text) = html2Text( f.read() )
			if self.title.strip() == "":
				self.title = self.url

			(self.ratio, diff, self.info) = checkUpdate( self.text, text )
			self.text = text
			if self.ratio > 0:
				self.date = date
				self.diff = diff
				return True
			else:
				return False


	def updateSafe( self, *args ):
		try:
			return self.update( *args )
		except urllib2.HTTPError, err:
			self.info = "Error: HTTP %d" % err.code
		except urllib2.URLError:
			self.info = "Error: URI"
		except socket.timeout:
			self.info = "Error: timeout"
		except sgmllib.SGMLParseError:
			self.info = "Error: invalid HTML"
		#except StandardError:
		#	self.info = "Error: unknown"

		return False
