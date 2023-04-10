import math #math import so we can use the pi value

class PipeSection:

    def __init__(self, n, fF, sL, d, iRG):
        #identifying information for each pipe section given in problem statement
        self.name = n #string to identify the pipe section, e.g. "AB"
        self.frictionFactor = fF #friction factor of this pipe section
        self.sectionLength = sL #length of this pipe section
        self.diameter = d #diameter of this pipe section
        self.initialRateGuess = iRG #initial flow rate guess

        #data we need to keep track of for each object for each iteration 
        self.headLossHistory = [] #list of the iterated values of head loss
        self.qHistory = [] #list of the iterated values of Q (each time we calculate a dQ, we add that dQ and add a new item to the list)
        self.qHistory.append(iRG) #adds the initial flow rate guess as the first iterated value of Q
        self.dQ = 0.0

        #calculate and define the constant k from the data given
        self.kConst = (8*fF*sL)/(9.81*pow(math.pi,2)*pow(d,5))

    def printData(self):
        print("name: " + self.name)
        print("friction factor: " + str(self.frictionFactor))
        print("section length: " + str(self.sectionLength))
        print("diameter: " + str(self.diameter))
        print("initial rate guess: " + str(self.initialRateGuess))
        print("kConst: " + str(self.kConst))
    
    def getKConst(self):
        return self.kConst

    def getName(self):
        return self.name
    
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
    
    def getDQ(self):
        return self.dQ

    def setDQ(self,num):
        self.dQ = num