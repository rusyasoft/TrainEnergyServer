import Sensor

class SensorNode(object):
   def __init__(self, sensornid, sensornodename, isalive):
      self.sensorNodeId = sensornid
      self.sensors = dict()
      self.sensorNodeName = sensornodename
      self.is_alive = isalive

   def setCurrentStatus(self, isalive, inp_sensors ): #isalive:bool, inp_sensors: list of Sensor
      self.is_alive = isalive
      #if isalive == True:
      print 'len(inp_sensors) = ', len(inp_sensors)
      print 'inp_sensors:', inp_sensors
      print 'self.sensors:', self.sensors
      for s_name in inp_sensors:
         print "s_name= ",s_name
         print "sensorname, sensor :", inp_sensors[s_name].sensorname, inp_sensors[s_name].measurement, inp_sensors[s_name].value #, inp_sensors[s_id]
         if s_name in self.sensors:
            print "using existing Sensor.Sensor"
            self.sensors[s_name].sensorname = inp_sensors[s_name].sensorname
            self.sensors[s_name].measurement = inp_sensors[s_name].measurement
            self.sensors[s_name].value = inp_sensors[s_name].value
         else:
            print "creation of New Sensor.Sensor"
            self.sensors[s_name] = Sensor.Sensor(inp_sensors[s_name].sensorname, inp_sensors[s_name].measurement, inp_sensors[s_name].value)
         #self.sensors[s_]

   def dummyTempHumStatus(self, isalive):
      self.is_alive = isalive
      self.sensorNodeId = 1313
      self.sensorNodeName = 'TempHum'
      self.sensors['temp'] = Sensor.Sensor('temp', 'farenheit',13)
      self.sensors['hum'] = Sensor.Sensor('hum', '%', 13)

   #def addSensor(sens):
   #   self.sensors.append(sens)


