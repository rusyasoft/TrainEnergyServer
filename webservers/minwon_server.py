from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os
import json
from pymongo import MongoClient
import paho.mqtt.client as mqtt
import threading

#connect mongodb 
mongo_client = MongoClient('energy.openlab.kr', 27017)
db = mongo_client.keti_energy_db.UserMinwon




subway_wrap = dict()
subw = dict()
subway_list = list()

####### ar[0] ###########
subw['Area'] = 'Gwangju'
subw['Location'] = '102'
subw['T1_1'] = 11
subw['T1_2'] = 12
subw['T1_3'] = 13

subw['T2_1'] = 21
subw['T2_2'] = 22
subw['T2_3'] = 23

subw['T3_1'] = 31
subw['T3_2'] = 32
subw['T3_3'] = 33

subw['T4_1'] = 41
subw['T4_2'] = 42
subw['T4_3'] = 43

subw['Train'] = 1919
subw['work'] = 0

subw['_id'] = '0000'

subway_list.append(subw)

####### ar[1] ###########
subw['Area'] = 'Gwangju'
subw['Location'] = '101'
subw['T1_1'] = 11
subw['T1_2'] = 12
subw['T1_3'] = 13

subw['T2_1'] = 21
subw['T2_2'] = 22
subw['T2_3'] = 23

subw['T3_1'] = 31
subw['T3_2'] = 32
subw['T3_3'] = 33

subw['T4_1'] = 41
subw['T4_2'] = 42
subw['T4_3'] = 43

subw['Train'] = 1010
subw['work'] = 1

subw['_id'] = '0001'


subway_list.append(subw)


subway_wrap['subway'] = subway_list

# main code

######## mqtt connection and messaging functions #########
def on_mqtt_connect(client, userdata, flags, rc):
        print "Connected to MQTT Broker with result code", str(rc)

        client.subscribe("/keti/energy/statusrequest")
        print "subscribed for /keti/energy/statusrequest"

def on_mqtt_message(client, userdata, msg):
        if msg.topic == "/keti/energy/statusrequest":
                client.publish("/keti/energy/systemstatus", '{"nodename":"MinwonServer", "status":"on"}')



global mqtt_client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_mqtt_connect
mqtt_client.on_message = on_mqtt_message

mqtt_client.connect('117.16.136.173', 1883, 600)

class KETI_HTTPRequestHandler(BaseHTTPRequestHandler):
   def do_GET(self):
      self.send_response(200)
      self.send_header('Content-type','text/html')
      self.end_headers()
      self.wfile.write(#'<form action="/profile/index/sendmessage" method="post" enctype="application/x-www-form-urlencoded">' +
		'<div class="upload_form">' +
    		'<dt id="message-label"><label class="optional" for="message">Enter Message</label></dt>' +
		'<dd id="message-element">' +
		'<textarea cols="80" rows="50" id="message" name="message">' +
		'</textarea></dd> <dt id="id-label">&nbsp;</dt> <dt id="send_message-label">&nbsp;</dt> <dd id="send_message-element">' +
		'<input type="submit" class="sendamessage" value="Send" id="send_message" name="send_message"></dd>' +
		'</div>' +
		#'</form>' +
		'<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js"></script>' +
		'<script type="text/javascript"> $("input.sendamessage").click(function(event) { event.preventDefault();' +
		"var message = $('textarea#message').val(); var id      = $('input#id').val();" +
		'url = "http://energy.openlab.kr:4000/"; ' +
		'var posting = $.post(url, message); ' +
		'posting.done(function( data ) { alert(message); }); }); </script>' )
      #self.wfile.write(json.dumps(subway_wrap))
      return

   def _set_headers(self):
      self.send_response(200)
      self.send_header('Content-type', 'text/html')
      self.end_headers()

   def do_POST(self):
      self._set_headers()
      self.data_string = self.rfile.read(int(self.headers['Content-Length']))
      print "in post method, data_string:", self.data_string
      
      try:
         o = json.loads(self.data_string)
      except:
         self.send_response(400)
         self.end_headers()
         return 
     
      self.send_response(200)
      self.end_headers()


      data = json.loads(self.data_string)
      #with open("test1234.json", "a") as outfile:
      #   json.dump(data, outfile)
      global mqtt_client
      mqtt_client.publish("/keti/energy/minwon", self.data_string)

      # storing in MongoDB
      db.insert(data)

      print "{}".format(data)
      #f = open("for_presen.py")
      #self.wfile.write(f.read())
      self.wfile.write("result")
      return


######## mqtt connection and messaging functions #########
#def on_mqtt_connect(client, userdata, flags, rc):
#	print "Connected to MQTT Broker with result code", str(rc)
#	
#	client.subscribe("/keti/energy/statusrequest")
#	print "subscribed for /keti/energy/statusrequest"
#
#def on_mqtt_message(client, userdata, msg):
#	if msg.topic == "/keti/energy/statusrequest":
#		client.publish("/keti/energy/systemstatus", '{"nodename":"MinwonServer", "status":"on"}')

# main code
#mqtt_client = mqtt.Client()
#mqtt_client.on_connect = on_mqtt_connect
#mqtt_client.on_message = on_mqtt_message
#
#mqtt_client.connect('117.16.136.173', 1883, 600)

def MQTTStarterThread():
   mqtt_client.loop_start()


# starting webSocket Server
t = threading.Thread(target = MQTTStarterThread())
t.start()



#connect mongodb
#mongo_client = MongoClient('energy.openlab.kr', 27017)
#db = mongo_client.keti_energy_db.UserMinwon

print "http server is starting ..."
server_address = ("", 4000)

httpd = HTTPServer(server_address, KETI_HTTPRequestHandler)
print ('http server is running ...')

httpd.serve_forever()

