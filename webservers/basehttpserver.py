from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os
import json


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

class KETI_HTTPRequestHandler(BaseHTTPRequestHandler):
   def do_GET(self):
      self.send_response(200)
      self.send_header('Content-type','text/html')
      self.end_headers()
      #self.wfile.write("Hello World!!!!")
      self.wfile.write(json.dumps(subway_wrap))
      return


# main code
print "http server is starting ..."
server_address = ("", 3000)

httpd = HTTPServer(server_address, KETI_HTTPRequestHandler)
print ('http server is running ...')

httpd.serve_forever()

