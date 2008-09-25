import threading
import Queue
#import logging


class Runner( object ):

	def __init__( self, procs, n ):
		self.queue = Queue.Queue()
		for proc in procs:
			self.queue.put( proc )

		self.threads = []
		try:
			for _ in xrange( n ):
				thr = threading.Thread( target = self._threadProc )
				thr.start()
				self.threads.append( thr )
		except StandardError:
			# XXX
			self.cancel()
			#self.join()
			raise
		

	def join( self ):
		for thr in self.threads:
			thr.join()


	def cancel( self ):
		while True:
			try:
				self.queue.get_nowait()
			except Queue.Empty:
				break


	def _threadProc( self ):
		while True:
			try:
				proc = self.queue.get_nowait()
			except Queue.Empty:
				break

			#try:
			#	proc()
			#except Exception, err:
			#	logging.error( str( err ) )
			proc()
