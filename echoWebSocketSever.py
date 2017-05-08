
from time import sleep
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

import threading

remote_client = dict()

def worker():
   print 'Worker'
   #return
   i = 3
   sleep(10)
   while i>0:
      sleep(3)
      if len(remote_client)>0:
         print 'helloo sent (size of remote_client = ', len(remote_client)
         for id in remote_client:
            remote_client[id].sendMessage(u'helloo')
         #print 'helloo sent (size of remote_client = ', len(remote_client)
         i -= 1
   print 'Worker Done!'

threads = []

class SimpleEcho(WebSocket):
   def handleMessage(self):

      i = 10
      #while i>0:
      #   sleep(3)
      #   self.sendMessage(self.data)
      #   print 'sent message'
      #   i -= 1
      self.sendMessage(self.data)

   def handleConnected(self):
      print self.address, 'connected', 'address[0] = ', self.address[0]
   
      #remote_client.append(self)
      remote_client[self.address] = self
      t = threading.Thread(target=worker)
      t.start()
      #for client in clients:
      #    client.sendMessage(self.address[0] + u' - connected')

   def handleClose(self):
      del remote_client[self.address]
      print self.address, 'closed'


server = SimpleWebSocketServer('', 8000, SimpleEcho)

#t = threading.Thread(target=worker)
#t.start()

#i = 10
#sleep(10)
#while i>0:
#   sleep(10)
#   remote_client[0].sendMessage('helloo')


server.serveforever()



