
def parseTrainDirection(inpstr):
   #print 'inpstr at parseTrainDirection :', inpstr
   strTrainNum, _dir = inpstr.strip().split('_')
   intTrainNum = int(strTrainNum)
   dir = 1 if _dir=='d' else 2
   return intTrainNum, dir


def parseTimeLine(_inpstr, scheduleTable, subwaysAr):
   inpstr = _inpstr.strip().split(',')
   sub_time = inpstr[0]
   trains = list()
   for index in range(1,len(inpstr)):
      #print 'inpstr[index]:', inpstr[index]
      if inpstr[index] != '0':
         intTrainNum, intDir = parseTrainDirection(inpstr[index])
         trains.append([subwaysAr[index-1], intTrainNum, intDir])
   scheduleTable[sub_time] = trains

def requestCurrentStatus(timeInpStr, scheduleTable):

   try:
      #check timeInpStr being time:
      hour, minute = map(int, timeInpStr.strip().split(':'))
      if timeInpStr in scheduleTable:
         return scheduleTable[timeInpStr]
      else:
         print 'Schedule does not contain this kind of number'
         return None

   except ValueError:
      print 'Oops! , parsing the time throw an error: ', timeInpStr
      return None

   #return scheduleTable[timeInpStr]



fi = open('schedule.csv', 'r')


str_startTime, str_stopTime = fi.readline().strip().split(',')
#print 'startTime:', str_startTime, 'stopTime:', str_stopTime

numOfSubways, numOfTimes = map(int,fi.readline().strip().split(','))

stationAr = map(int, fi.readline().strip().split(','))
_subwaysAr = fi.readline().strip().split(',')
subwaysAr = map(int, _subwaysAr[1:])

scheduleTable = dict()
for _ in range(numOfTimes):
   rline = fi.readline()
   #print 'at for cycle:', rline
   parseTimeLine(rline, scheduleTable, subwaysAr)

#print 'ANSWER'
#print scheduleTable

# query section
print 'Enter the time:',
curtime = raw_input()
print requestCurrentStatus(curtime, scheduleTable)






