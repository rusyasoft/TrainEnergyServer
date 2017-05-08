#!/usr/bin/env python
# -*- coding: utf-8 -*-

from openpyxl import load_workbook

import threading

import os.path
import ExcelFileWatcher
import ExcelFileValidator
import ServerConfiguration
import ExcelFileLoader

def test_callback(evpath, evname):
	print "test_callback: evpath=", evpath, "evname = ", evname
	excelfileloader = ExcelFileLoader.ExcelFileLoader()
	trainIDs = excelfileloader.loadfile(evpath+'/'+evname)

	for l in trainIDs:
        	print l


########## main ##############

serverConfiguration = ServerConfiguration.ServerConfiguration('server.cfg')
foldername = serverConfiguration.getExcelFolderNameForSchedule()
filename = serverConfiguration.getExcelFileNameForSchedule()

print 'Folder=  ',foldername, ' filename= ', filename

excelfileloader = ExcelFileLoader.ExcelFileLoader()
trainIDs = excelfileloader.loadfile(foldername+'/'+filename)

for l in trainIDs:
        print l

print 'Starting the file validator ...'
#excelFileValidator = ExcelFileValidator.ExcelFileValidator( foldername, filename , test_callback) #("webservers/excelsrc", "excel1.xlsx", test_callback)

def ExcelFileValidatorThreadStarter():
	excelFileValidator = ExcelFileValidator.ExcelFileValidator( foldername, filename , test_callback) #("webservers/excelsrc", "excel1.xlsx", test_callback)
	excelFileValidator.startFileWatcher()

#excelFileValidatorThread = threading.Thread(target = ExcelFileValidatorThreadStarter())

#excelFileValidatorThread.daemon = True

#excelFileValidatorThread.start()

excelFileValidator = ExcelFileValidator.ExcelFileValidator( foldername, filename , test_callback) #("webservers/excelsrc", "excel$
excelFileValidator.startFileWatcher()

print "Right after thread start !!!"


	

#
#excelfileloader = ExcelFileLoader.ExcelFileLoader()
#trainIDs = excelfileloader.loadfile(folername+'/'+filename)
#
#for l in trainIDs:
#	print l
#
#excelFileWatcher.start_watch_loop()
