#!/usr/bin/env python
# -*- coding: utf-8 -*-

#changelog: 20170420 - adding file watcher and reactor

from flask import Flask
from gevent.wsgi import WSGIServer


import paho.mqtt.client as mqtt
import json
import threading

import Train
import SensorNode
import Sensor
import BigScheduleTable

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

import time
from time import sleep
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from pymongo import MongoClient

######### excel processing related classes ###########
import os.path
import ExcelFileWatcher
import ExcelFileValidator
import ServerConfiguration
import ExcelFileLoader


app = Flask(__name__)


######## excel processing related global variable, callbackfunction and functions ######
global NUMBER_OF_SENSORS
NUMBER_OF_SENSORS = 24

#trainNum2ID = dict() # dictionary that will contain train Number and ID mapping table
def convertTrainList2Dict(trainIDlist):
	trainDict = dict()	
	for val1, val2 in trainIDlist:
		trainDict[int(val1)] = int(val2)

	print "result of convertion from list of trains to dicitionary ->", trainDict
	return trainDict
		


serverConfiguration = ServerConfiguration.ServerConfiguration('server.cfg') # load Server Configuration from server.cfg
Excel_foldername = serverConfiguration.getExcelFolderNameForSchedule()
Excel_filename = serverConfiguration.getExcelFileNameForSchedule()

print 'Excel Folder =', Excel_foldername, 'and filename =', Excel_filename

excelFileLoader = ExcelFileLoader.ExcelFileLoader()
#trainIDList = excelFileLoader.loadfile(Excel_foldername + '/' + Excel_filename)
trainNum2ID = excelFileLoader.loadfile(Excel_foldername + '/' + Excel_filename)
print 'TrainNum2ID: ', trainNum2ID

#### another quick fix -> converting back from trainID to trainNum
ID2TrainNum = dict()
for t in trainNum2ID:
    ID2TrainNum[trainNum2ID[t]] = t
print 'ID2TrainNum: ', ID2TrainNum
##################################################################


#trainNum2ID = convertTrainList2Dict(trainIDList)

# in order to start file validator that will watch the we need to create new thread

def excelFileChanged_callback(evpath, evname):
	global trainNum2ID
	print "new Excel File has been uploaded: newpath=", evpath, "new file name = ", evname

	# saving folder and filenames into configuration file
	serverConfiguration.setExcelFileNameForSchedule(evname)


	excelfileloader = ExcelFileLoader.ExcelFileLoader()
	trainIDs = excelfileloader.loadfile(evpath+'/'+evname)
	#TODO: convert trainIDs to trainNum2ID
	trainNum2ID = convertTrainList2Dict(trainIDs)

	for l in trainNum2ID:
		print str(l) + "->" + str(trainNum2ID[l])

#def ExcelFileValidatorThreadStarter():
#	excelFileValidator = ExcelFileValidator.ExcelFileValidator( Excel_foldername, Excel_filename , excelFileChanged_callback)

excelFileValidator = ExcelFileValidator.ExcelFileValidator( Excel_foldername, Excel_filename , excelFileChanged_callback)
excelFileValidator.startFileWatcher()

#excelFileValidatorThread  = threading.Thread(target = ExcelFileValidatorThreadStarter())
#excelFileValidatorThread.start()
#try:
#	thread.start_new_thread(ExcelFileValidatorThreadStarter)
#	print "Excel File Validator Thread is started !"
#except:
#	print "Error: unable to start Excel File Validator thread"


#############################################################################



remote_web_socket_clients = dict()

def on_connect(client, userdata, flags, rc):
   print "Connected to MQTT Broker with result code ", str(rc)

   #client.subscribe("/keti/energy/fromgw")
   #client.subscribe("/keti/energy/statusrequest", 1)
   #client.subscribe("/keti/energy/fromtguserapp")
   print "Subscribed to topic /keti/energy/fromgw"

#Trains = dict() #dictionaries of Train, key is trainID

# load the Big Train schedule table
bigTable = BigScheduleTable.BigScheduleTable()
bigTable.loadFromCSV('schedule.csv')


###### Trains should be initialized with dummy data #######
Trains = bigTable.initializeTrainTables(NUMBER_OF_SENSORS)



##########################################
# query example to bigTable
#
# bigTable.requestCurrentStatus('15:06')
#########################################


############### http webserver class declaration ############

def wrapSubwayTotalInfo(Trains, bigTable, str_curtime):  # str_curtime must be "hh:mm" format
   #test flag for checking zero value
   testFlag = 1


   json_response = ""
   schedule_list = bigTable.requestCurrentStatus(str_curtime)

   #temporary temp
   temporary_temp_int = 10 + int(time.strftime("%M"))%10
   temporary_hum_int = 10 + int(time.strftime("%M"))%10 # just for distinguishing with temporary_temp_int
   # if None is returned as a schedule_list then dont bother to do further processing
   # just return no Train Available at this time
   if schedule_list == None:
      # pass
      return '{"response_msg": "No Subway available at this time"}'

   subway_wrap = dict()
   subway_list = list()

   for sublocdir in schedule_list:
      subw = dict()
      #converting to subwayID
      subwayNum = trainNum2ID[int(sublocdir[0])]

      stationNum = sublocdir[1]
      dir = sublocdir[2] - 1
    
      if subwayNum in Trains:
         print 'subway is detected'
         subw['Area'] = 'Gwangju'
         subw['Location'] = stationNum

         # TODO: now its just fixed somehow, but the logic should be reconsidered
         curTrain_SensorNodes = Trains[subwayNum].sensorNodes
         print 'Number of SensorNodes in this train:', len(curTrain_SensorNodes)
         listofTemperatureSensors = list()
         listofHumiditySensors = list()
         for sensors in curTrain_SensorNodes:
            listofTemperatureSensors.append(curTrain_SensorNodes[sensors].sensors['temp'])
            listofHumiditySensors.append(curTrain_SensorNodes[sensors].sensors['hum'])
         
         numofnecessaryDummyTemps = NUMBER_OF_SENSORS - len(listofTemperatureSensors)

         #temporary temperature
         for i in range(numofnecessaryDummyTemps):
            temporarySensor = Sensor.Sensor('temp', 'celsius', temporary_temp_int)
            listofTemperatureSensors.append(temporarySensor)
            temporaryHumiditySensor = Sensor.Sensor('hum', '%', temporary_hum_int)
            listofHumiditySensors.append(temporaryHumiditySensor)

         subw['T1_1'] = listofTemperatureSensors[0].value
         subw['T1_2'] = listofTemperatureSensors[1].value
         subw['T1_3'] = listofTemperatureSensors[2].value

         subw['T2_1'] = listofTemperatureSensors[3].value
         subw['T2_2'] = listofTemperatureSensors[4].value
         subw['T2_3'] = listofTemperatureSensors[5].value

         subw['T3_1'] = listofTemperatureSensors[6].value
         subw['T3_2'] = listofTemperatureSensors[7].value
         subw['T3_3'] = listofTemperatureSensors[8].value

         subw['T4_1'] = listofTemperatureSensors[9].value
         subw['T4_2'] = listofTemperatureSensors[10].value
         subw['T4_3'] = listofTemperatureSensors[11].value

         ########## new style is added ######
         subw['T1ID'] = 1000 + (subwayNum%100)
         subw['T1TEMP'] = listofTemperatureSensors[0].value
         subw['T1HUM'] = listofHumiditySensors[0].value

         subw['T2ID'] = 1100 + (subwayNum%100)
         subw['T2TEMP'] = listofTemperatureSensors[3].value
         subw['T2HUM'] = listofHumiditySensors[3].value

         subw['T3ID'] = 1200 + (subwayNum%100)
         subw['T3TEMP'] = listofTemperatureSensors[6].value
         subw['T3HUM'] = listofHumiditySensors[6].value

         subw['T4ID'] = 1700 + (subwayNum%100)
         subw['T4TEMP'] = listofTemperatureSensors[9].value
         subw['T4HUM'] = 0
         
         ###################################
         subw['Train'] = subwayNum
         subw['work'] = dir #Trains[subwayNum].movingDirection - 1
         subw['_id'] = '1111'
      else:
         print 'subway is not detected, subwayNum = ', subwayNum
         subw['Area'] = 'Gwangju'
         subw['Location'] = stationNum

         # TODO: now its just fixed somehow, but the logic should be reconsidered
         curTrain_SensorNodes = SensorNode.SensorNode(NUMBER_OF_SENSORS+1, 'TempHum', False)  #Trains[subwayNum].sensorNodes

         listofTemperatureSensors = list()
         listofHumiditySensors = list()
         #for sensors in curTrain_SensorNodes:
         #   print 'curTrain_SensorNodes=>', curTrain_SensorNodes[sensors].sensors
         #   listofTemperatureSensors.append(curTrain_SensorNodes[sensors].sensors['temp'])

         numofnecessaryDummyTemps = NUMBER_OF_SENSORS - len(listofTemperatureSensors)
         for i in range(numofnecessaryDummyTemps):
            temporarySensor = Sensor.Sensor('temp', 'celsius', temporary_temp_int)
            listofTemperatureSensors.append(temporarySensor)
            temporaryHumiditySensor = Sensor.Sensor('hum', '%', temporary_hum_int)
            listofHumiditySensors.append(temporaryHumiditySensor)

         subw['T1_1'] = listofTemperatureSensors[0].value
         subw['T1_2'] = listofTemperatureSensors[1].value
         subw['T1_3'] = listofTemperatureSensors[2].value

         subw['T2_1'] = listofTemperatureSensors[3].value
         subw['T2_2'] = listofTemperatureSensors[4].value
         subw['T2_3'] = listofTemperatureSensors[5].value

         subw['T3_1'] = listofTemperatureSensors[6].value
         subw['T3_2'] = listofTemperatureSensors[7].value
         subw['T3_3'] = listofTemperatureSensors[8].value

         subw['T4_1'] = listofTemperatureSensors[9].value
         subw['T4_2'] = listofTemperatureSensors[10].value
         subw['T4_3'] = listofTemperatureSensors[11].value

         ########## new style is added ######
         subw['T1ID'] = 1000 + (subwayNum%100)
         subw['T1TEMP'] = listofTemperatureSensors[0].value
         subw['T1HUM'] = listofHumiditySensors[0].value

         subw['T2ID'] = 1100 + (subwayNum%100)
         subw['T2TEMP'] = listofTemperatureSensors[3].value
         subw['T2HUM'] = listofHumiditySensors[0].value
 
         subw['T3ID'] = 1200 + (subwayNum%100)
         subw['T3TEMP'] = listofTemperatureSensors[6].value
         subw['T3HUM'] = listofHumiditySensors[6].value

         subw['T4ID'] = 1700 + (subwayNum%100)
         subw['T4TEMP'] = listofTemperatureSensors[9].value
         subw['T4HUM'] = listofHumiditySensors[9].value
         ###################################

         #REMOVE IT AFTER TEST: this is test code in order to check the zero value
         if testFlag > 0:
            subw['T1ID'] = 1000 + (subwayNum%100)
            subw['T1TEMP'] = 0
            subw['T1HUM'] = 0

            subw['T2ID'] = 1100 + (subwayNum%100)
            subw['T2TEMP'] = 0
            subw['T2HUM'] = 0
 
            subw['T3ID'] = 1200 + (subwayNum%100)
            subw['T3TEMP'] = 0
            subw['T3HUM'] = 0

            subw['T4ID'] = 1700 + (subwayNum%100)
            subw['T4TEMP'] = 0
            subw['T4HUM'] = 0
            testFlag -= 1
         ###############################

         subw['Train'] = subwayNum
         subw['work'] = dir #Trains[subwayNum].movingDirection - 1
         subw['_id'] = '1111'
      subway_list.append(subw)

   subway_wrap['subway'] = subway_list
   json_response = json.dumps(subway_wrap)
   
   return json_response

SubwayListCaching = dict()
def wrapSubwayTotalInfoCaching(Trains, bigTable, reqtime):
    print 'reqtime = ', str(reqtime)
    if str(reqtime) not in SubwayListCaching:
        SubwayListCaching[str(reqtime)] = wrapSubwayTotalInfo(Trains, bigTable, reqtime)
    
    return SubwayListCaching[str(reqtime)]
    

@app.route("/")
def mainserver():
    #return wrapSubwayTotalInfo(Trains, bigTable, time.strftime("%H:%M"))
    return wrapSubwayTotalInfoCaching(Trains, bigTable, time.strftime("%H:%M"))
    

@app.route("/Gwangju/Temperature")
def mainserver2():
    #return wrapSubwayTotalInfo(Trains, bigTable, time.strftime("%H:%M"))
    return wrapSubwayTotalInfoCaching(Trains, bigTable, time.strftime("%H:%M"))


class KETI_HTTPRequestHandler(BaseHTTPRequestHandler):
   def do_GET(self):
      self.send_response(200)
      self.send_header('Content-type','text/html')
      self.end_headers()
      #self.wfile.write("Hello World!!!!")
      #jsondumps = wrapSubwayTotalInfo(Trains, bigTable, "10:33")
      jsondumps = wrapSubwayTotalInfo(Trains, bigTable, time.strftime("%H:%M"))
      
      self.wfile.write(jsondumps) #json.dumps(subway_wrap))
      return


def on_message_statusrequest(client, userdata, msg):
    client.publish("/keti/energy/systemstatus", '{"nodename":"MainServer", "status":"on"}', 1)

def on_message_fromtguserapp(client, userdata, msg):
    jsondumps = wrapSubwayTotalInfo(Trains, bigTable, time.strftime("%H:%M"))
    client.publish("/keti/energy/totguserapp", jsondumps)

def on_message_fromgw(client, userdata, msg):
    print "fromgw: ", msg.topic, " ->", msg.payload
    try:
        o = json.loads(msg.payload)
        tid = ID2TrainNum[int(o["TrainID"])] #string type converted to int
        #print 'trainID = ', tid
        liveness = False
        if o["Status"]=="On":
            liveness = True
   
        sNode = SensorNode.SensorNode(jsonPayload=msg.payload)

        if tid in Trains:
            #print "use existing TRAIN------------------------"
            Trains[tid].setSensorNodeStatus(liveness, sNode)
        else:
            #print 'Create new TRAIN++++++++++++++++++++++++++++'
            Trains[tid] = Train.Train(tid)
            Trains[tid].setSensorNodeStatus(liveness, sNode)

        # mongoDB related operations
        userdata.insert(o)
        #results = userdata.find()
        #for record in results:
        #   print 'record = ', record

        if len(remote_web_socket_clients)>0:
            for id in remote_web_socket_clients:
                remote_web_socket_clients[id].sendMessage(unicode(msg.payload))
            print 'Message sent to WebSocketClients'

    except:
        print "exception happend at on_message_fromgw()"

def on_message(client, userdata, msg):
   print msg.topic,"->", str(msg.payload)

def deprecated_on_message(client, userdata, msg):
   # check for the status request message
   if msg.topic=="/keti/energy/statusrequest":
      client.publish("/keti/energy/systemstatus", '{"nodename":"MainServer", "status":"on"}', 1)
      return 
   if msg.topic =="/keti/energy/fromtguserapp":
      jsondumps = wrapSubwayTotalInfo(Trains, bigTable, time.strftime("%H:%M"))/keti/energy/fromtguserapp
      client.publish("/keti/energy/totguserapp", jsondumps)
      return
   print msg.topic,"->", str(msg.payload)

   # the case: /keti/energy/fromgw

   o = json.loads(msg.payload)


   #debugging purpose
   #print 'o=',o

   #playing with Train class
   #print 'sensorID = ', o["SensorID"]
   tid = int(o["TrainID"]) #string type converted to int
   #print 'trainID = ', tid

   liveness = False
   if o["Status"]=="On":
      liveness = True
   
   sNode = SensorNode.SensorNode(jsonPayload=msg.payload)

   if tid in Trains:
      #print "use existing TRAIN------------------------"
      Trains[tid].setSensorNodeStatus(liveness, sNode)
   else:
      #print 'Create new TRAIN++++++++++++++++++++++++++++'
      Trains[tid] = Train.Train(tid)
      Trains[tid].setSensorNodeStatus(liveness, sNode)

   # testing wrapSubwayTotalInfo function
   #jsondumps = wrapSubwayTotalInfo(Trains, bigTable, "15:03")
   #print 'jsondumps =>',jsondumps

   """ Temperarily off """

   # mongoDB related operations
   userdata.insert(o)
   #results = userdata.find()
   #for record in results:
   #   print 'record = ', record

   if len(remote_web_socket_clients)>0:
      for id in remote_web_socket_clients:
         remote_web_socket_clients[id].sendMessage(unicode(msg.payload))
      print 'Message sent to WebSocketClients'
   """ """

###### defining SimpleEcho class here ###
class WebSocketReceiver(WebSocket):
   def handleMessage(self):
      #do nothing yet
      pass
   def handleConnected(self):
      print self.address, 'connected', 'address=',self.address[0],':',self.address[1]
      remote_web_socket_clients[self.address] = self

   def handleClose(self):
      del remote_web_socket_clients[self.address]
      print self.address, 'closed'
#########################################



def MQTTStarterThread():
   print "mqtt thread starting"
   mqtt_client.loop_start()
   print "mqtt thread started"

def KETI_HTTPServerThread():
   print('KETI http server is starting ...')
   server_address = ("", 3001)
   httpd = HTTPServer(server_address, KETI_HTTPRequestHandler)
   print('KETI http server is running ...')
   httpd.serve_forever()
   print('KETI http server is stoped !')


# starting webSocket Server
#t = threading.Thread(target = WebSocketServerThread())
#t.start()
#print 'WebSocket Server Started ...'

#remote_web_socket_clients = dict()

mongo_client = MongoClient('117.16.136.173', 27017)
db = mongo_client.keti_energy_db.temphumCOL
#db = mongo_client.test.temprustam


mqtt_client = mqtt.Client(userdata=db)

mqtt_client.message_callback_add("/keti/energy/statusrequest/#", on_message_statusrequest)
mqtt_client.message_callback_add("/keti/energy/fromtguserapp/#", on_message_fromtguserapp)
mqtt_client.message_callback_add("/keti/energy/fromgw/#", on_message_fromgw)



mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect('117.16.136.173', 1883, 600)

res = mqtt_client.subscribe("/keti/energy/#")


#client = MongoClient('117.16.136.173', 27017)


#db = client.keti_energy
#collection = db.keti_energy

#db = client.keti_energy.temphumCOL



#db.

#results = db.find()

#for record in results:
#   print record

#mongo_client.close()


# starting webSocket Server
t = threading.Thread(target = MQTTStarterThread())
#t.setDaemon(True)
t.start()


"""
keti_http_t = threading.Thread(target = KETI_HTTPServerThread)
print 'Starting WebSocket Server'
server = SimpleWebSocketServer('', 8000, WebSocketReceiver)
print 'WebSocket Server Started ...'
keti_http_t.start()
# starting exel file validator
#excelFileValidator = ExcelFileValidator.ExcelFileValidator( foldername, filename , test_callback)
# forever loop started in main thread
server.serveforever()
#mqtt_client.loop_forever()
mongo_client.close()
"""

if __name__ == '__main__':
    #app.run(
    #    host="0.0.0.0",
    #    port=int("3001")
    #)
    http_server= WSGIServer(('', 3001), app)
    http_server.serve_forever()


#print 'Starting MQTT...'
#mqtt_client.loop_start()
#print 'Closing MongoDB Connection ...'
#mongo_client.close()
