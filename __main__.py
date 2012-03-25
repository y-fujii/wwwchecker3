# by y.fujii <y-fujii at mimosa-pudica.net>, public domain


from __future__ import division
from __future__ import with_statement
import sys
import socket
import threading
import cgi
import time
import pickle
import codecs
import random
import webbrowser
import parallel
import config
import wwwInfo


def median( xs ):
	n = len( xs )
	ys = sorted( xs )
	assert n > 0
	if n % 2 == 0:
		return (ys[n // 2 - 1] + ys[n // 2]) / 2.0
	else:
		return ys[n // 2]


def renderHTML( out, infos, config ):
	out.write( config.htmlHeader )
	for info in infos:
		def color( cn, c0, c1 ):
			w = min( info.ratio, config.maxRatio )
			if w == 0:
				(rr, gg, bb) = cn
			else:
				rr = w * (c1[0] - c0[0]) / config.maxRatio + c0[0]
				gg = w * (c1[1] - c0[1]) / config.maxRatio + c0[1]
				bb = w * (c1[2] - c0[2]) / config.maxRatio + c0[2]

			return '#%02x%02x%02x' % (rr, gg, bb)

		tm = time.localtime( info.date )
		summary = "<br />\n".join( cgi.escape( l ) for l in info.diff[:config.maxLine] )
		out.write(
			config.htmlContent % {
				"fgColor": color( *config.fgColor ),
				"bgColor": color( *config.bgColor ),
				"uriColor": color( *config.uriColor ),
				"yyyy": tm[0],
				"mo": tm[1],
				"dd": tm[2],
				"hh": tm[3],
				"mi": tm[4],
				"status": cgi.escape( info.status ),
				"url": cgi.escape( info.url ),
				"title": cgi.escape( info.title ),
				"summary": summary,
			}
		)

	out.write( config.htmlFooter )


def main():
	with file( config.listFile ) as f:
		urls = f.read().splitlines()
	try:
		with file( config.infoFile ) as f:
			oldInfos = pickle.load( f )
	except StandardError:
		oldInfos = []
	
	infoDict = dict( (t.url, t) for t in oldInfos )
	def f( url ):
		if url in infoDict:
			return infoDict[url]
		else:
			return wwwInfo.URLInfo( url )
	newInfos = [ f( url ) for url in urls ]
	random.shuffle( newInfos )

	socket.setdefaulttimeout( config.timeOut )

	lock = threading.Lock()
	times = []
	def update( info ):
		bgnTime = time.time()
		wwwInfo.updateSafe( info )
		endTime = time.time()
		with lock:
			times.append( endTime - bgnTime )
			sys.stdout.write( "\r\x1b[K" + info.url )
			sys.stdout.flush()

	runner = parallel.Runner(
		[ lambda i = i: update( i ) for i in newInfos ],
		config.nParallel,
	)
	try:
		runner.join()
	except:
		runner.abort()
		raise

	sys.stdout.write(
		"\r\x1b[K%.1f ms / sites (median)\n" % (median( times ) * 1000.0)
	)
	sys.stdout.flush()

	newInfos.sort( key = lambda x: -x.date )
	with file( config.infoFile, "w" ) as f:
		pickle.dump( newInfos, f )

	with file( config.htmlFile, "w" ) as f:
		out = codecs.getwriter( "utf-8" )( f )
		renderHTML( out, newInfos, config )

	webbrowser.open( config.htmlFile )


if __name__ == "__main__":
	try:
		main()
	except StandardError:
		sys.stdout.write( "Error.\n" )