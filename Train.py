
import SensorNode

class Train(object):
   def __init__(self, tid):
      self.trainID = 0
      self.sensorNodes = dict()
      self.currentStationNum = 0
      self.movingDirection = 1

   def setTrainStatus(self, curStation, movDir):
      self.currentStationNum = curStation
      self.movingDirection = movDir

   def setSensorNodeStatus(self, isalive, sensorNode): #sensorNode: SensorNode 
      if sensorNode.sensorNodeId in self.sensorNodes:
         #TODO: hope there is no problem at overwriting existing dictionary value again and again
         print("setSensorNodeStatus sensorNode Exist")
         self.sensorNodes[sensorNode.sensorNodeId].setCurrentStatus(isalive, sensorNode.sensors)
      else:
         print("setSensorNodeStatus sensorNode not Exist")
         self.sensorNodes[sensorNode.sensorNodeId] = sensorNode
         


   def addSensorNode(self, sensorNode):
      self.sensorNodes.append(sensorNode)

   def getSensorNodes(self):
      return self.sensorNodes


#example
#snid = 6
#sNodeName = "TempHum"
#sNode = SensorNode.SensorNode(snid, sNodeName, True)

