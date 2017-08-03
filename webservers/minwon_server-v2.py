#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request
from gevent.wsgi import WSGIServer

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os
import json
from pymongo import MongoClient
import paho.mqtt.client as mqtt
import threading

########### 400 Bad Request ###########
class InvalidUsage(Exception):
    status_code = 400
    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv
#######################################


app = Flask(__name__)

## register an error handler
@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

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

        client.subscribe("/keti/energy/statusrequest",1)
        print "subscribed for /keti/energy/statusrequest"

def on_mqtt_message(client, userdata, msg):
        if msg.topic == "/keti/energy/statusrequest":
            client.publish("/keti/energy/systemstatus", '{"nodename":"MinwonServer", "status":"on"}',1)


			

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
         print "Exception happened: ", self.data_string
         self.send_response(400)
         self.end_headers()
         return 
     
      self.send_response(200)
      self.end_headers()
      if "type" in o:
         if o["type"] == '2':
            self.wfile.write("The Survey Successfully Received!\n")
         else:
            self.wfile.write("The Complaint Successfully Received!\n")
            global mqtt_client
            mqtt_client.publish("/keti/energy/minwon", bytearray(self.data_string) )
      else:
         self.wfile.write("The Complaint Successfully Received!\n")


      data = json.loads(self.data_string)
      #with open("test1234.json", "a") as outfile:
      #   json.dump(data, outfile)

      # storing in MongoDB
      db.insert(data)

      print "result:", "{}".format(data)
      #f = open("for_presen.py")
      #self.wfile.write(f.read())
      #self.wfile.write("result")
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
mongo_client = MongoClient('energy.openlab.kr', 27017)
db = mongo_client.keti_energy_db.UserMinwon

print "http server is starting ..."
server_address = ("", 4001)

@app.route("/", methods=['GET','POST'])
def minwon_serve():
	if request.method == 'POST':
		print 'post: request.data = ',request.data
		return_msg = ""
		try:
			o = json.loads(request.data)
			#self.send_response(200)
			#self.end_headers()
			if "type" in o:
				if o["type"] == '2':
					return_message = "The Survey Successfully Received!\n"
				else:
					return_message = "The Complaint Successfully Received!!\n"
					global mqtt_client
					mqtt_client.publish("/keti/energy/minwon", bytearray(request.data) )
			else:
				return_message = "The Complaint Successfully Received!!!\n"	
			# storing in MongoDB
			db.insert(o)
		except:
			print "Exception happened: ", request.data
			return "HTTP/1.0 400 Bad Request\nServer: BaseHTTP/0.3 Python/2.7.6\nDate: Wed, 19 Jul 2017 06:33:17 GMT\n", 400
		return_message = "HTTP/1.0 200 OK\nServer: BaseHTTP/0.3 Python/2.7.6\nDate: Wed, 19 Jul 2017 06:33:17 GMT\n\n" + return_message
		return return_message

	elif request.method == 'GET':
		print 'get: request.data = ',request.data
	else:
		print "request.method = ", request.method
		
	return "returning_messge"

#httpd = HTTPServer(server_address, KETI_HTTPRequestHandler)
#print ('http server is running ...')
#httpd.serve_forever()

if __name__ == '__main__':
	http_server = WSGIServer(('', 4000), app)
	http_server.serve_forever()
