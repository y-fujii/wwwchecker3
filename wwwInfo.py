# by y.fujii <y-fujii at mimosa-pudica.net>, public domain

from __future__ import with_statement
import contextlib
import StringIO
import gzip
import socket
import httplib
import urllib2
from email import Utils
import time
import difflib
import sgmllib
import html2text


class URLInfo( object ):

	def __init__( self, url ):
		self.url = url
		self.text = []
		self.date = 0
		self.size = -1
		self.ratio = 0
		self.status = ""
		self.diff = []
		self.title = url


def testUpdate( old, new ):
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


def update( info, testUpdate = testUpdate, html2Text = html2text.html2Text ):
	req = urllib2.Request( info.url, headers = {
		"if-modified-since": Utils.formatdate( info.date ),
		"accept-encoding": "gzip",
	} )
	try:
		f = urllib2.urlopen( req )
	except urllib2.HTTPError, err:
		if err.code == 304:
			info.status = "If-modified-since"
			info.ratio = 0
			return False
		else:
			raise

	with contextlib.closing( f ):
		if "last-modified" in f.info():
			date = Utils.mktime_tz(
				Utils.parsedate_tz( f.info()["last-modified"] )
			)
			if date == info.date:
				info.status = "Last-modified"
				info.ratio = 0
				return False
		else:
			date = time.time()

		if "content-length" in f.info():
			size = f.info()["content-length"]
			if size == info.size:
				info.status = "Content-length"
				info.ratio = 0
				return False
		else:
			size = -1

		if f.info().get( "content-encoding", "" ) == "gzip":
			html = gzip.GzipFile( fileobj = StringIO.StringIO( f.read() ) ).read()
		else:
			html = f.read()

	(title, text) = html2Text( html )
	(info.ratio, diff, info.status) = testUpdate( info.text, text )
	info.size = size
	info.text = text
	if title.strip() != "":
		info.title = title
	else:
		info.title = info.url

	if info.ratio > 0:
		info.date = date
		info.diff = diff
		return True
	else:
		return False


def updateSafe( info, *args ):
	try:
		info.ratio = 0
		return update( info, *args )
	except urllib2.HTTPError, err:
		info.status = "Error: HTTP %d" % err.code
	except urllib2.URLError:
		info.status = "Error: invalid URL"
	except httplib.HTTPException:
		info.status = "Error: invalid HTTP"
	except socket.timeout:
		info.status = "Error: timeout"
	except sgmllib.SGMLParseError:
		info.status = "Error: invalid HTML"
	except ValueError:
		info.status = "Error: invalid URL"
	#except StandardError:
	#	info.status = "Error: unknown"
