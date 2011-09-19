# by y.fujii <y-fujii at mimosa-pudica.net>, public domain

import threading
import Queue


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
		except:
			self.__del__()
			raise
	

	def __del__( self ):
		try:
			self.abort()
		except: pass
	

	def abort( self ):
		self.cancel()
		self.join() # ...
		

	def join( self ):
		# http://bugs.python.org/issue1167930
		while any( t.isAlive() for t in self.threads ):
			for thr in self.threads:
				thr.join( 1 )


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
			proc()
