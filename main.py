#!/usr/bin/env python

from __future__ import with_statement
import sys
import socket
import threading
import cgi
import time
import pickle
import codecs
import webbrowser
import misc
import parallel
import config
import wwwInfo


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

	socket.setdefaulttimeout( 30 )

	stdoutLock = threading.Lock()
	def update( info ):
		info.updateSafe()
		with stdoutLock:
			sys.stdout.write( info.url + "\n" )
			sys.stdout.flush()

	# One can call runner.cancel() from other thread to stop this safely.
	# But the process can not receive signals during runner.join().
	# So we make the thread as daemon mode...
	runner = parallel.Runner(
		[ lambda i = i: update( i ) for i in newInfos ],
		config.nParallel,
		True,
	)
	with misc.disposing( runner ):
		runner.join()

	newInfos.sort( key = lambda x: -x.date )
	with file( config.infoFile, "w" ) as f:
		pickle.dump( newInfos, f )

	with file( config.htmlFile, "w" ) as f:
		outs = codecs.getwriter( "utf-8" )( f )
		outs.write( config.htmlHeader )
		for info in newInfos:
			def color( r, g, b ):
				w = max( 8 - info.ratio, 0 )
				rr = r + w * (255 - r) / 16
				gg = g + w * (255 - g) / 16
				bb = b + w * (255 - b) / 16
				return '#%02x%02x%02x' % (rr, gg, bb)

			tm = time.localtime( info.date )
			summary = "<br />\n".join( cgi.escape( l ) for l in info.diff[:4] )
			outs.write(
				config.htmlContent % {
					"fgColor": color( *config.fgColor ),
					"bgColor": color( *config.bgColor ),
					"uriColor": color( *config.uriColor ),
					"yyyy": tm[0],
					"mo": tm[1],
					"dd": tm[2],
					"hh": tm[3],
					"mi": tm[4],
					"info": cgi.escape( info.info ),
					"url": cgi.escape( info.url ),
					"title": cgi.escape( info.title ),
					"summary": summary,
				}
			)

		outs.write( config.htmlFooter )

	webbrowser.open( config.htmlFile )


if __name__ == "__main__":
	main()
