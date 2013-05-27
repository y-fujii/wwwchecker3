# by Yasuhiro Fujii <y-fujii at mimosa-pudica.net>, public domain

import math
import contextlib
import re
import io
import gzip
import urllib.request
import urllib.error
import http.client
from email import utils
import time
import difflib
import html2text


class UrlInfo( object ):

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
	size = len( old ) + len( new )
	if size == 0:
		return (0, [], "-0000 +0000")
	lls = [ math.log( len( tn ) ) for (tn, ta) in old + new ]
	rts = [ len( ta ) / len( tn ) for (tn, ta) in old + new ]
	lavg = sum( lls ) / size
	ravg = sum( rts ) / size
	# XXX: / (N - 1)
	lsgm = math.sqrt( sum( l * l for l in lls ) / size - lavg * lavg )
	rsgm = math.sqrt( sum( r * r for r in rts ) / size - ravg * ravg )

	def calcScore( tn, ta ):
		llen = math.log( len( tn ) )
		rate = len( ta ) / len( tn )
		return (rate - ravg) / (rsgm + 1e-8) + (llen - lavg) / (lsgm + 1e-8)

	oldA = [ re.sub( "[0-9]+", "0", ta ) for (tn, ta) in old ]
	newA = [ re.sub( "[0-9]+", "0", ta ) for (tn, ta) in new ]
	opcodes = difflib.SequenceMatcher( None, oldA, newA, autojunk = False ).get_opcodes()

	nIns = 0
	nDel = 0
	text = []
	for (tag, i1, i2, j1, j2) in opcodes:
		if tag in ["delete", "replace"]:
			if any( calcScore( tn, ta ) >= 0.0 for (tn, ta) in old[i1:i2] ):
				nDel += i2 - i1
		if tag in ["insert", "replace"]:
			if any( calcScore( tn, ta ) >= 0.0 for (tn, ta) in new[j1:j2] ):
				nIns += j2 - j1
				text.extend( tn for (tn, ta) in new[j1:j2] if ta != "" )

	return (
		max( nIns, nDel ),
		text,
		"-%04d +%04d" % (nDel, nIns),
	)


def update( info, testUpdate = testUpdate, html2Text = html2text.html2Text ):
	req = urllib.request.Request( info.url, headers = {
		"if-modified-since": utils.formatdate( info.date ),
		"accept-encoding": "gzip",
	} )
	try:
		f = urllib.request.urlopen( req )
	except urllib.error.HTTPError as err:
		if err.code == 304:
			info.status = "If-modified-since"
			info.ratio = 0
			return False
		else:
			raise

	with contextlib.closing( f ):
		if "last-modified" in f.info():
			date = utils.mktime_tz(
				utils.parsedate_tz( f.info()["last-modified"] )
			)
			if date == info.date:
				info.status = "Last-modified"
				info.ratio = 0
				return False
		else:
			date = time.time()

		if "content-length" in f.info():
			size = int( f.info()["content-length"] )
			if size == info.size:
				info.status = "Content-length"
				info.ratio = 0
				return False
		else:
			size = -1

		if f.info().get( "content-encoding", "" ) == "gzip":
			html = gzip.GzipFile( fileobj = io.BytesIO( f.read() ) ).read()
		else:
			html = f.read()

	if size < 0:
		size = len( html )

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
	except urllib.error.HTTPError as err:
		info.status = "Error: HTTP %d" % err.code
	except http.client.HTTPException:
		info.status = "Error: Protocol"
	except OSError:
		info.status = "Error: I/O"
	except ValueError:
		info.status = "Error: invalid URL"

	return False
