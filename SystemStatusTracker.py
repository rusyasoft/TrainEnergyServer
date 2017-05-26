import paho.mqtt.client as mqtt
import json
import threading

#from time import sleep
import time
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

#remote_web_socket_clients = dict()

def on_connect(client, userdata, flags, rc):
   print "Connected to MQTT Broker with result code ", str(rc)

   client.subscribe("/keti/energy/systemstatus")
   print "Subscribed to topic /keti/energy/systemstatus"

def on_message(client, userdata, msg):
   print msg.topic,"->", str(msg.payload)

   """
   o = json.loads(msg.payload)
   print 'o=',o
   userdata.insert(o)
   if len(remote_web_socket_clients)>0:
      for id in remote_web_socket_clients:
         remote_web_socket_clients[id].sendMessage(unicode(msg.payload))
      print 'Message sent to WebSocketClients'
   """


###### defining SimpleEcho class here ###
class SimpleEcho(WebSocket):
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

def MqttServerThread():
   #server = SimpleWebSocketServer('', 8000, SimpleEcho)
   #server.serveforever()
   #mqtt_client.loop_forever()
   mqtt_client.loop_start()

# starting webSocket Server
#t = threading.Thread(target = WebSocketServerThread())
#t.start()
#print 'WebSocket Server Started ...'

mqtt_client = mqtt.Client() #userdata=db)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect('117.16.136.173', 1883, 600)


def StatusRequesterThread():
   while True:
      print 'about to send request'
      time.sleep(5)
      print 'about to send request2'
      mqtt_client.publish("/keti/energy/statusrequest", "status_request_msg")
      print 'request sent'

#t = threading.Thread(target = StatusRequesterThread())
#print 'Status Requester Thread has started..'
#t.start()

t = threading.Thread(target = MqttServerThread())
#t.setDaemon(True)
t.start()

#t = threading.Thread(target = StatusRequesterThread())
#print 'Status Requester Thread has started..'
#t.start()

#print 'Starting WebSocket Server'
#server = SimpleWebSocketServer('', 8000, SimpleEcho)
#print 'WebSocket Server Started ...'
#server.serveforever()

#mqtt_client.loop_forever()

StatusRequesterThread()
