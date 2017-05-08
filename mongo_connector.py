import paho.mqtt.client as mqtt
import json
from pymongo import MongoClient

def on_connect(client, userdata, flags, rc):
   print "Connected with result code ", str(rc)

   client.subscribe("/keti/energy/fromgw")

def on_message(client, userdata, msg):
   print msg.topic,"->", str(msg.payload)
   o = json.loads(msg.payload)
   userdata.insert(o)
   #results = userdata.find()
   #for record in results:
   #   print 'record = ', record


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

mqtt_client.loop_forever()

mongo_client.close()
