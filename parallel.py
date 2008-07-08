import logging
import threading
import Queue


def run( procs, n ):
	queue = Queue.Queue()
	for proc in procs:
		queue.put( proc )

	thrs = []
	for _ in xrange( n ):
		def threadProc():
			while True:
				try:
					proc = queue.get_nowait()
				except Queue.Empty:
					break

				try:
					proc()
				except Exception, err:
					logging.error( str( err ) )

		thr = threading.Thread( target = threadProc )
		thr.start()
		thrs.append( thr )
	
	for thr in thrs:
		thr.join()
