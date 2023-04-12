from decimal import *

#class to create an object for each point/junction in the pipe network
class PipePoint:

    def __init__(self, n, f):
        self.name = n
        self.flowInOut = f
    
    def getName(self):
        return self.name

    def getFlow(self):
        return self.flowInOut