import os
import os.path
from pyinotify import WatchManager, IN_DELETE, IN_CREATE, IN_CLOSE_WRITE, ProcessEvent, Notifier, ThreadedNotifier
import pyinotify
import subprocess
import sys
import re
import argparse
import fnmatch

"""
class PatternAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, fnmatch.translate(values))

parser = argparse.ArgumentParser(description='Launch a script if specified files change.')
parser.add_argument('directory', help='the directory which is recursively monitored')

group = parser.add_mutually_exclusive_group()
group.add_argument('-r', '--regex', required=False, default=".*", help='files only trigger the reaction if their name matches this regular expression')
group.add_argument('-p', '--pattern', required=False, dest="regex", action=PatternAction, help='files only trigger the reaction if their name matches this shell pattern')

parser.add_argument("script", help="the script that is executed upon reaction")

class Options:
    __slots__=["directory", "regex", "script"]

options = Options()
args = parser.parse_args(namespace=options)
"""



	

class Reload (Exception):
    pass



class ExcelFileWatcher(object):

	class Process(ProcessEvent):
    #def __init__(self,  options):
    #    self.regex = re.compile(options.regex)
    #    self.script = options.script
	
		def __init__(self, folderpath,  event_callback):
			#self.regex = re.compile(options.regex)
			#self.script = options.script
			self.event_callback = event_callback
			self.folderpath = folderpath

		def process_IN_CREATE(self, event):
			target = os.path.join(event.path, event.name)
			print "create event happened!"
			if os.path.isdir(target):
				raise Reload()

		def process_IN_DELETE(self, event):
			print "delete event happened"
			raise Reload()

		def process_IN_CLOSE_WRITE(self, event):
			target = os.path.join(event.path, event.name)
			#print "target = ", target
			#print 'event.path = ', event.path
			#print 'event.name = ', event.name
			self.event_callback(event.path, event.name)
			#if self.regex.match(target):
			#    args = self.script.replace('$f', target).split()
			#    os.system("clear")
			#    sys.stdout.write("executing script: " + " ".join(args) + "\n")
			#    subprocess.call(args)
			#    sys.stdout.write("------------------------\n")

	def __init__(self, folderpath,  event_callback ):
		self.event_callback = event_callback
		self.folderpath = folderpath

	def start_watch_loop(self):
		wm = WatchManager()
		process = self.Process(self.folderpath, self.event_callback) #options)
		self.notifier = ThreadedNotifier(wm, process) #Notifier(wm, process)

		#notifier = Notifier(wm)
		mask = IN_DELETE | IN_CREATE | IN_CLOSE_WRITE
		#wdd = wm.add_watch(options.directory, mask, rec=True)
		#wm.add_watch('./excelsrc', mask, rec=True)
		wm.add_watch('./'+self.folderpath, mask, rec=True)
		
		self.notifier.start()

		"""	
		while True:
			wm = WatchManager()
			process = self.Process(self.folderpath, self.event_callback) #options)
			notifier = ThreadedNotifier(wm, process) #Notifier(wm, process)
			#notifier = Notifier(wm)

			mask = IN_DELETE | IN_CREATE | IN_CLOSE_WRITE
			#wdd = wm.add_watch(options.directory, mask, rec=True)
			#wm.add_watch('./excelsrc', mask, rec=True)
			wm.add_watch('./'+self.folderpath, mask, rec=True)

			try:
				while True:
					print '.'
					notifier.process_events()
					print '+'
					if notifier.check_events():
						notifier.read_events()
					print '-'
			except Reload:
				pass
			except KeyboardInterrupt:
				notifier.stop()
				break
		"""
	def stop_watch_loop(self):
		self.notifier.stop()

			
# test code
"""
def callbackjan(evpath, evname):
	print 'evpath = ', evpath
	print 'evname = ', evname
		
excelFileWatcher = ExcelFileWatcher(callbackjan)
excelFileWatcher.start_watch_loop()
"""
