
import os.path
import ExcelFileWatcher

import threading

class ExcelFileValidator(object):

	#def local_callback_func(evpath, evname):
	#print "local_callback_func has triggered! evpath=", evpath, "evname=", evname
	#self.upper_level_callback_func(evpath, evname)

	def __init__(self, folderpath, filename, callback_func):
		print "file existence check ... 1"
		self.upper_level_callback_func = callback_func
		print "file existence check ... 2"
		if os.path.isfile(folderpath+'/'+filename):
			print "file exists: ", folderpath+'/'+filename
			self.excelFileWatcher = ExcelFileWatcher.ExcelFileWatcher(folderpath, self.local_callback_func)
			#print 'Start file watching ...'			
			#excelFileWatcher.start_watch_loop()

		else:
			print "file does not exists: ", folderpath + '/' + filename
	def startFileWatcher(self):
		print 'Start file watching ...'
		self.excelFileWatcher.start_watch_loop()

	def local_callback_func(self, evpath, evname):
                print "local_callback_func has triggered! evpath=", evpath, "evname=", evname
                self.upper_level_callback_func(evpath, evname)


#test code
"""
def test_callback(evpath, evname):
	print "test_callback: evpath=", evpath, "evname = ", evname

print 'Starting the file validator ...'
excelFileValidator = ExcelFileValidator("excelsrc/excel1.xlsx", test_callback)
"""
#excelFileWatcher.start_watch_loop()
