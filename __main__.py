# by Yasuhiro Fujii <y-fujii at mimosa-pudica.net>, public domain

import sys
import socket
import threading
import html
import time
import pickle
import random
import webbrowser
import urllib3
import parallel
import wwwInfo
import config


def renderHtml( out, infos, config ):
	out.write( config.htmlHeader )
	for info in infos:
		def color( cn, c0, c1 ):
			w = min( info.ratio, config.maxRatio )
			if w == 0:
				(rr, gg, bb) = cn
			else:
				rr = w * (c1[0] - c0[0]) // config.maxRatio + c0[0]
				gg = w * (c1[1] - c0[1]) // config.maxRatio + c0[1]
				bb = w * (c1[2] - c0[2]) // config.maxRatio + c0[2]

			return '#%02x%02x%02x' % (rr, gg, bb)

		tm = time.localtime( info.date )
		summary = "<br />\n".join( html.escape( l ) for l in info.diff[:config.maxLine] )
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
				"status": html.escape( info.status ),
				"url": html.escape( info.url ),
				"title": html.escape( info.title ),
				"summary": summary,
			}
		)

	out.write( config.htmlFooter )


def main():
	with open( config.listFile ) as f:
		urls = f.read().splitlines()
	try:
		with open( config.infoFile, "rb" ) as f:
			oldInfos = pickle.load( f )
	except IOError:
		oldInfos = []
	
	infoDict = dict( (t.url, t) for t in oldInfos )
	def f( url ):
		try:
			return infoDict[url]
		except KeyError:
			return wwwInfo.UrlInfo( url )
	newInfos = [ f( url ) for url in urls ]
	random.shuffle( newInfos )

	urllib3.disable_warnings()
	http = urllib3.PoolManager( config.nParallel, timeout = config.timeOut )

	lock = threading.Lock()
	count = 0
	times = []
	def update( info ):
		nonlocal count
		bgnTime = time.time()
		wwwInfo.update( info, http )
		endTime = time.time()
		with lock:
			count += 1
			times.append( endTime - bgnTime )
			sys.stdout.write(
				f"{count:5} / {len( newInfos )} | "
				f"{1000.0 * (endTime - bgnTime):5.0f} [ms] | "
				f"{info.url}\n"
			)

	runner = parallel.Runner(
		[ lambda i = i: update( i ) for i in newInfos ],
		config.nParallel,
	)
	try:
		runner.join()
	except:
		runner.abort()
		raise

	times.sort()
	q1 = 1000.0 * times[round( 0.25 * len( times ) )]
	q2 = 1000.0 * times[round( 0.50 * len( times ) )]
	q3 = 1000.0 * times[round( 0.75 * len( times ) )]
	sys.stdout.write(
		f"Q1 = {q1:.0f}, Q2 = {q2:.0f}, Q3 = {q3:.0f} [ms].\n"
	)

	newInfos.sort( key = lambda x: -x.date )
	with open( config.infoFile, "wb" ) as f:
		pickle.dump( newInfos, f )

	with open( config.htmlFile, "w" ) as f:
		renderHtml( f, newInfos, config )

	webbrowser.open_new_tab( config.htmlFile )


if __name__ == "__main__":
	main()
