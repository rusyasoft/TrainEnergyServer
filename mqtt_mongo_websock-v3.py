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




remote_web_socket_clients = dict()

def on_connect(client, userdata, flags, rc):
   print "Connected to MQTT Broker with result code ", str(rc)

   client.subscribe("/keti/energy/fromgw")
   print "Subscribed to topic /keti/energy/fromgw"

Trains = dict() #dictionaries of Train, key is trainID

# load the Big Train schedule table
bigTable = BigScheduleTable.BigScheduleTable()
bigTable.loadFromCSV('schedule.csv')


###### Trains should be initialized with dummy data #######

def initializeTrainTables(Trains, bigTable):

   for trainID in bigTable.subwayIds:
      subwayNum = trainID      
      Trains[subwayNum] = Train.Train(subwayNum)

      #adding 12 dummy sensor nodes
      for i in range(1,13):
         curTrain_DummySensorNode = SensorNode.SensorNode(i, 'TempHum', False)
         curTrain_DummySensorNode.sensors['temp'] = Sensor.Sensor('temp', 'farenheit', 13)
         curTrain_DummySensorNode.sensors['hum'] = Sensor.Sensor('hum', '%', 13)
         Trains[subwayNum].sensorNodes[i] = curTrain_DummySensorNode


   #subway_wrap['subway'] = subway_list

###########################################################
initializeTrainTables(Trains, bigTable)



##########################################
# query example to bigTable
#
# bigTable.requestCurrentStatus('15:06')
#########################################


############### http webserver class declaration ############

def wrapSubwayTotalInfo(Trains, bigTable, str_curtime):  # str_curtime must be "hh:mm" format
   json_response = ""
   schedule_list = bigTable.requestCurrentStatus(str_curtime)

   subway_wrap = dict()
   #subw = dict()
   subway_list = list()

   #print 'schedule_list = ', schedule_list

   for sublocdir in schedule_list:
      subw = dict()
      subwayNum = sublocdir[0]
      stationNum = sublocdir[1]
      dir = sublocdir[2] - 1
    
      print 'sublocdir', sublocdir
      print 'Trains =>', Trains 

      if subwayNum in Trains:
         print 'subway is detected'
         subw['Area'] = 'Gwangju'
         subw['Location'] = stationNum

         # TODO: now its just fixed somehow, but the logic should be reconsidered
         curTrain_SensorNodes = Trains[subwayNum].sensorNodes
         print 'Number of SensorNodes in this train:', len(curTrain_SensorNodes)
         listofTemperatureSensors = list()
         for sensors in curTrain_SensorNodes:
            print 'curTrain_SensorNodes=>', curTrain_SensorNodes[sensors].sensors
            listofTemperatureSensors.append(curTrain_SensorNodes[sensors].sensors['temp'])
         
         numofnecessaryDummyTemps = 12-len(listofTemperatureSensors)
         for i in range(numofnecessaryDummyTemps):
            temporarySensor = Sensor.Sensor('temp', 'farenheit', 13)
            listofTemperatureSensors.append(temporarySensor)

         print 'len of listofTemperatureSensors =>', len(listofTemperatureSensors)

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

         subw['Train'] = subwayNum
         subw['work'] = dir #Trains[subwayNum].movingDirection - 1

         subw['_id'] = '1111'
      
      else:
         print 'subway is not detected'
         subw['Area'] = 'Gwangju'
         subw['Location'] = stationNum

         

         # TODO: now its just fixed somehow, but the logic should be reconsidered
         curTrain_SensorNodes = SensorNode.SensorNode(13, 'TempHum', False)  #Trains[subwayNum].sensorNodes
         #print 'Number of SensorNodes in this train:', len(curTrain_SensorNodes)
         listofTemperatureSensors = list()
         #for sensors in curTrain_SensorNodes:
         #   print 'curTrain_SensorNodes=>', curTrain_SensorNodes[sensors].sensors
         #   listofTemperatureSensors.append(curTrain_SensorNodes[sensors].sensors['temp'])

         numofnecessaryDummyTemps = 12-len(listofTemperatureSensors)
         for i in range(numofnecessaryDummyTemps):
            temporarySensor = Sensor.Sensor('temp', 'farenheit', 13)
            listofTemperatureSensors.append(temporarySensor)

         print 'len of listofTemperatureSensors =>', len(listofTemperatureSensors)

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

         subw['Train'] = subwayNum
         subw['work'] = dir # #Trains[subwayNum].movingDirection - 1

         subw['_id'] = '1111'


      subway_list.append(subw)

   subway_wrap['subway'] = subway_list
   print 'subway_wrap=>', subway_wrap
   json_response = json.dumps(subway_wrap)
   
   return json_response


class KETI_HTTPRequestHandler(BaseHTTPRequestHandler):
   def do_GET(self):
      self.send_response(200)
      self.send_header('Content-type','text/html')
      self.end_headers()
      #self.wfile.write("Hello World!!!!")
      #jsondumps = wrapSubwayTotalInfo(Trains, bigTable, "15:03")
      jsondumps = wrapSubwayTotalInfo(Trains, bigTable, time.strftime("%H:%M"))
      
      self.wfile.write(jsondumps) #json.dumps(subway_wrap))
      return




def on_message(client, userdata, msg):
   print msg.topic,"->", str(msg.payload)
   o = json.loads(msg.payload)


   #debugging purpose
   print 'o=',o

   #playing with Train class
   print 'sensorID = ', o["SensorID"]
   tid = int(o["TrainID"]) #string type converted to int
   print 'trainID = ', tid

   liveness = False
   if o["Status"]=="On":
      liveness = True

   snid = int(o["SensorID"])
   sNodeName = o["SensorName"]
   sNode = SensorNode.SensorNode(snid, sNodeName, liveness)

   #process sensors modules inside single sensorNode
   if sNodeName=="TempHum": # if the the sensor node is TempHum then it caries temp and hum sensor modules

      sensorModules = dict()

      sname = "temp"
      smeasurement = "farenheit"
      svalue = o["temp"]
      print 'temp=>', svalue
      #tempSensor = Sensor(sname, smeasurement, svalue)
      sensorModules[sname] =  Sensor.Sensor(sname, smeasurement, svalue)

      sname = "hum"
      smeasurement = "%"
      svalue = o["hum"]
      #humSensor = Sensor(sname, smeasurement, svalue)
      sensorModules[sname] = Sensor.Sensor(sname, smeasurement, svalue)

      sNode.setCurrentStatus(liveness, sensorModules)
      print 'sensorModules:',sensorModules
      print 'sNode is set', sNode.sensors
      

   if tid in Trains:
      print "use existing TRAIN------------------------"
      Trains[tid].setSensorNodeStatus(liveness, sNode)
   else:
      print 'Create new TRAIN++++++++++++++++++++++++++++'
      Trains[tid] = Train.Train(tid)
      Trains[tid].setSensorNodeStatus(liveness, sNode)

   print 'Trains->',Trains


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
   #server = SimpleWebSocketServer('', 8000, SimpleEcho)
   #server.serveforever()
   #mqtt_client.loop_forever()
   mqtt_client.loop_start()

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
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect('117.16.136.173', 1883, 60)



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

keti_http_t = threading.Thread(target = KETI_HTTPServerThread)

print 'Starting WebSocket Server'
server = SimpleWebSocketServer('', 8000, WebSocketReceiver)
print 'WebSocket Server Started ...'
keti_http_t.start()

server.serveforever()




#mqtt_client.loop_forever()

mongo_client.close()
