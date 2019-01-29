# by Yasuhiro Fujii <y-fujii at mimosa-pudica.net>, public domain

import itertools
import collections
import math
import contextlib
import re
from email import utils
import time
import difflib
import html2text
import urllib3


class UrlInfo( object ):

	def __init__( self, url ):
		self.url = url
		self.text = []
		self.date = 0
		self.size = 0
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

	oldTx = [ re.sub( r"[0-9][0-9,]*(\.[0-9]+)?", "0", tn ) for (tn, ta) in old ]
	newTx = [ re.sub( r"[0-9][0-9,]*(\.[0-9]+)?", "0", tn ) for (tn, ta) in new ]
	opcodes = difflib.SequenceMatcher( None, oldTx, newTx, autojunk = False ).get_opcodes()

	counter = collections.defaultdict( int )
	for tx in itertools.chain( oldTx, newTx ):
		counter[tx] += 1

	nIns = 0
	nDel = 0
	text = []
	for (tag, i1, i2, j1, j2) in opcodes:
		if tag == "replace" and i2 - i1 == 1 and j2 - j1 == 1:
			continue
		if tag in ["delete", "replace"]:
			tmp = [ old[i] for i in range( i1, i2 ) if counter[oldTx[i]] == 1 ]
			if any( calcScore( tn, ta ) >= 0.0 for (tn, ta) in tmp ):
				nDel += len( tmp )
		if tag in ["insert", "replace"]:
			tmp = [ new[i] for i in range( j1, j2 ) if counter[newTx[i]] == 1 ]
			if any( calcScore( tn, ta ) >= 0.0 for (tn, ta) in tmp ):
				nIns += len( tmp )
				text.extend( tn for (tn, ta) in tmp )

	return (
		max( nIns, nDel ),
		text,
		"-%04d +%04d" % (nDel, nIns),
	)


def update( info, http, testUpdate = testUpdate, html2Text = html2text.html2Text ):
	headers = {
		"accept-encoding": "gzip, deflate",
		"user-agent": "Mozilla/5.0 (+http://mimosa-pudica.net/www-checker.html)",
	}
	if info.etag is None:
		headers["if-modified-since"] = utils.formatdate( info.date )
	else:
		headers["if-none-match"] = info.etag

	dateNow = time.time()
	try:
		f = http.request( "GET", info.url, headers = headers, preload_content = False )
	except KeyError:
		info.status = "Invalid URL"
		info.ratio = 0
		return False
	except urllib3.exceptions.HTTPError:
		info.status = "Error"
		info.ratio = 0
		return False

	with contextlib.closing( f ):
		if f.status == 304:
			if info.etag is None:
				info.status = "If-modified-since"
			else:
				info.status = "If-none-match"
			info.ratio = 0
			return False
		elif f.status != 200:
			info.status = "HTTP %d" % f.status
			info.ratio = 0
			return False

		info.etag = f.headers.get( "etag", None )

		if "last-modified" in f.headers:
			try:
				date = utils.mktime_tz(
					utils.parsedate_tz( f.headers["last-modified"] )
				)
			except ValueError:
				date = dateNow

			if date == info.date:
				info.status = "Last-modified"
				info.ratio = 0
				return False
		else:
			date = dateNow

		try:
			size = int( f.headers.get( "content-length", "-1" ) )
		except ValueError:
			size = -1

		if size == info.size:
			info.status = "Content-length"
			info.ratio = 0
			return False

		try:
			html = f.read( decode_content = True )
		except urllib3.exceptions.HTTPError:
			info.status = "Error"
			info.ratio = 0
			return False

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
