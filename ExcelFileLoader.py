#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from openpyxl import load_workbook


class ExcelFileLoader(object):
	def __init__(self):
		self.trainIDcolumn = list()
	#	self.fullfilepath = fullfilepath
	def loadfile(self, fullfilepath):
		self.fullfilepath = fullfilepath
		self.wb = load_workbook(fullfilepath)

		#print wb.get_sheet_names()

		#sheet = wb.get_sheet_by_name('평일') #  'Sheet1')
		self.sheet = self.wb.worksheets[0]

		#print sheet.title

		#print '-------------'
#print sheet['B5'].value
		self.trainIDcolumn = list()

		print '------ this is what we need -------'
		for i in range(5,31):
			#print sheet.cell(row=i, column=2).value, sheet.cell(row=i, column=3).value
			self.trainIDcolumn.append( (self.sheet.cell(row=i, column=2).value, self.sheet.cell(row=i, column=3).value) )
		return self.trainIDcolumn

	def printTrainList(self):
		for l in self.trainIDcolumn:
			print l

