import math #math import so we can use the pi value
#from decimal import Decimal

class PipeSection:

    def __init__(self, pP1, pP2, fF, sL, d, iRG):
        #identifying information for each pipe section given in problem statement
        self.pipePoints = [pP1, pP2]  #list of two PipePoint objects to define where the pipe is located
        self.frictionFactor = fF #friction factor of this pipe section
        self.sectionLength = sL #length of this pipe section
        self.diameter = d #diameter of this pipe section
        self.initialRateGuess = iRG #initial flow rate guess

        #data we need to keep track of for each object for each iteration 
        self.headLossHistory = [float(0.0)] #list of the iterated values of head loss
        self.qHistory = [float(0.0)] #list of the iterated values of Q (each time we calculate a dQ, we add that dQ and add a new item to the list)
        self.qHistory.append(float(iRG)) #adds the initial flow rate guess as the first iterated value of Q
        self.dQHistory = [float(0.0)]

        #calculate and define the constant k from the data given
        self.kConst = (8*fF*sL)/(9.81*pow(math.pi,2)*pow(d,5))
        #self.kConst = decimal.Decimal.divide(Decimal.multiply(8,Decimal.multiply(fF,sL)), Decimal.multiply(9.81,Decimal.multiply(Decimal.power(math.pi,2), Decimal.power(d,5))))

        #add a "reversed" marker; false by default
        #indicates to other methods if the PipeSection in question is being viewed as flowing forwards or backwards
        self.reversed = False

    def printData(self):
        print("name: " + self.pipePoints[0].getName() + self.pipePoints[1].getName())
        print("friction factor: " + str(self.frictionFactor))
        print("section length: " + str(self.sectionLength))
        print("diameter: " + str(self.diameter))
        print("initial rate guess: " + str(self.initialRateGuess))
        print("kConst: " + str(self.kConst))
    
    def getKConst(self):
        return self.kConst

    def getPipePoints(self):
        return self.pipePoints
    
    def appendFlowRateHistory(self,num):
        self.flowRateHistory.append(num)

    def appendHeadLossHistory(self,num):
        self.headLossHistory.append(num)

    def appendQHistory(self,num):
        self.qHistory.append(num)
        
    def getRecentQVal(self):
        return self.qHistory[len(self.qHistory)-1]
    
    def getRecentHLVal(self):
        return self.headLossHistory[len(self.headLossHistory)-1]
    
    def getFrictionFactor(self):
        return self.frictionFactor
    
    def getLength(self):
        return self.sectionLength
    
    def getDiameter(self):
        return self.diameter
    
    def getInitialRateGuess(self):
        return self.initialRateGuess
    
    def getFullHeadLossHistory(self):
        return self.headLossHistory
    
    def getFullQHistory(self):
        return self.qHistory
    
    def getRecentDQ(self):
        return self.dQ[len(self.dQ)-1]

    def appendDQHistory(self,num):
        self.dQHistory.append(num)
    
    def getDQHistory(self):
        return self.dQHistory
    
    def getReversed(self):
        return self.reversed

    def setReversed(self, r):
        self.reversed = r