# by Yasuhiro Fujii <y-fujii at mimosa-pudica.net>, public domain

import math
import contextlib
import re
import io
import gzip
import zlib
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
		self.etag = None


def testUpdate( old, new ):
	ars = [ len( ta ) / len( tn ) for (tn, ta) in old + new ] + [ 0.0, 1.0 ]
	lls = [ math.log( len( tn ) ) for (tn, ta) in old + new ] + [ 0.0, 6.0 ]
	aavg = sum( ars ) / len( ars )
	lavg = sum( lls ) / len( lls )
	aisd = math.sqrt( (len( ars ) - 1) / sum( (v - aavg) * (v - aavg) for v in ars ) )
	lisd = math.sqrt( (len( lls ) - 1) / sum( (v - lavg) * (v - lavg) for v in lls ) )

	def calcScore( tn, ta ):
		assert tn != ""
		ll = math.log( len( tn ) )
		ar = len( ta ) / len( tn )
		return (ar - aavg) * aisd + (ll - lavg) * lisd

	oldTx = [ re.sub( r"[0-9]+", "0", tn ) for (tn, ta) in old ]
	newTx = [ re.sub( r"[0-9]+", "0", tn ) for (tn, ta) in new ]
	opcodes = difflib.SequenceMatcher( None, oldTx, newTx, autojunk = False ).get_opcodes()

	nIns = 0
	nDel = 0
	text = []
	for (tag, i1, i2, j1, j2) in opcodes:
		if tag == "replace" and i2 - i1 == 1 and j2 - j1 == 1:
			continue
		if tag in ["delete", "replace"]:
			if any( calcScore( tn, ta ) >= 0.0 for (tn, ta) in old[i1:i2] ):
				nDel += i2 - i1
		if tag in ["insert", "replace"]:
			if any( calcScore( tn, ta ) >= 0.0 for (tn, ta) in new[j1:j2] ):
				nIns += j2 - j1
				text.extend( tn for (tn, ta) in new[j1:j2] )

	return (
		max( nIns, nDel ),
		text,
		"-%04d +%04d" % (nDel, nIns),
	)


def update( info, testUpdate = testUpdate, html2Text = html2text.html2Text ):
	headers = {
		"accept-encoding": "gzip, deflate",
		"user-agent": "Mozilla/5.0 (+http://mimosa-pudica.net/www-checker.html)",
	}
	if info.etag is None:
		headers["if-modified-since"] = utils.formatdate( info.date )
	else:
		headers["if-none-match"] = info.etag

	try:
		f = urllib.request.urlopen(
			urllib.request.Request( info.url, headers = headers )
		)
	except urllib.error.HTTPError as err:
		if err.code == 304:
			if info.etag is None:
				info.status = "If-modified-since"
			else:
				info.status = "If-none-match"
			info.ratio = 0
			return False
		else:
			raise

	with contextlib.closing( f ):
		info.etag = f.info().get( "etag", None )

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

		data = f.read()
		cenc = f.info().get( "content-encoding", "" )
		if cenc == "gzip":
			html = gzip.GzipFile( fileobj = io.BytesIO( data ) ).read()
		elif cenc == "deflate":
			html = zlib.decompress( data )
		else:
			html = data

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
	except EOFError:
		info.status = "Error: EOF"
	except ValueError:
		info.status = "Error: invalid URL"

	return False
