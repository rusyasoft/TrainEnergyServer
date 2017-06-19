
import ConfigParser

class ServerConfiguration(object):
	def __init__(self, configFileName):
		self.cfgFileName = configFileName
		self.Config = ConfigParser.ConfigParser()
		

	def open(self):
		self.cfgfile = open(self.cfgFileName, 'w')
		

	def save(self):
		if self.cfgfile.closed == False:
			self.cfgfile.close()
			self.cfgfile.open()
		
			

	def close(self):
		if self.cfgfile.closed == False:
			self.cfgfile.close()
	
	

	def ConfigSectionMap(self, section):
		dict1 = {}
		options = self.Config.options(section)
		for option in options:
			try:
				dict1[option] = self.Config.get(section, option)
				if dict1[option] == -1:
					DebugPrint("skip: %s" % option)
			except:
				print("exception on %s!" % option)
				dict1[option] = None
		return dict1

	def getExcelFileNameForSchedule(self):
		self.Config.read(self.cfgFileName)
		#print self.Config.get('ExcelFiles', 'ScheduleInExcelFileName')
		return self.ConfigSectionMap('ExcelFiles')['schedulefilename']
	def getExcelFolderNameForSchedule(self):
		self.Config.read(self.cfgFileName)
		return self.ConfigSectionMap('ExcelFiles')['schedulefoldername']

	def setExcelFileNameForSchedule(self, sch_filename):
		cfgfile = open(self.cfgFileName, 'w')
		#self.Config.add_section('ExcelFiles')
		self.Config.set('ExcelFiles', 'ScheduleFileName', sch_filename)
		self.Config.write(cfgfile)
		cfgfile.close()

	def setExcelFoldernameForSchedule(self, sch_foldername):
		cfgfile = open(self.cfgFileName, 'w')
		#self.Config.add_section('ExcelFiles')
		self.Config.set('ExcelFiles', 'ScheduleFolderName', sch_foldername)
		self.Config.write(cfgfile)
		cfgfile.close()
		

"""
Config = ConfigParser.ConfigParser()
Config.read("tomorrow.ini")

cfgfile = open('next.ini', 'w')

print Config.sections()

Name = ConfigSectionMap('SectionOne')['name']
Age = ConfigSectionMap('SectionOne')['age']
print "Hello %s. You are %s years old"%(Name,Age)

Config.add_section('Person')
Config.set('Person', 'HasEyes', True)
Config.set('Person', 'Age', 50)
Config.write(cfgfile)
cfgfile.close()
"""


#serverConfiguration = ServerConfiguration('server.cfg')
#print 'Excel Filename =', serverConfiguration.getExcelFileNameForSchedule()


