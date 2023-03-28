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
        self.flowRateHistory = [] #list of the iterated values of flow rate
        self.headLossHistory = [] #list of the iterated values of head loss
        self.deltaQHistory = [] #list of the iterated values of dQ

        #calculate and define the constant k from the data given
        self.kConst = (8*fF*sL)/(9.81*pow(math.pi,2)*pow(d,5))

    def printData(self):
        print("name: " + self.name)
        print("friction factor: " + str(self.frictionFactor))
        print("section length: " + str(self.sectionLength))
        print("diameter: " + str(self.diameter))
        print("initial rate guess: " + str(self.initialRateGuess))
        print("kConst: " + str(self.kConst))