import sys

class Num:
    max = sys.maxint

    def __init__(self,num):
        self.n = num

    def getn(self):
        return self.n

    @staticmethod
    def getone():
        return 1

    @classmethod
    def getmax(cls):
        return cls.max

myObj = Num(3)
# with the appropriate decorator these should work fine
print myObj.getone()
print myObj.getmax()
print myObj.getn()


