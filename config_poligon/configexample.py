

import ConfigParser

def ConfigSectionMap(section):
	dict1 = {}
	options = Configcha.options(section)
	for option in options:
		try:
			dict1[option] = Configcha.get(section, option)
			if dict1[option] == -1:
				DebugPrint("skip: %s" % option)
		except:
			print("exception on %s!" % option)
			dict1[option] = None
	return dict1

		

Configcha = ConfigParser.ConfigParser()
Configcha.read("tomorrow.ini")

#cfgfile = open('next.ini', 'w')

#print Config.sections()

Name = ConfigSectionMap('SectionOne')['name']
Age = ConfigSectionMap('SectionOne')['age']
print "Hello %s. You are %s years old"%(Name,Age)


"""
Config.add_section('Person')
Config.set('Person', 'HasEyes', True)
Config.set('Person', 'Age', 50)
Config.write(cfgfile)
cfgfile.close()
"""
