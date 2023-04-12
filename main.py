#-------------------------------------IMPORT STATEMENTS AND GLOBAL VARIABLE DECLARATION---------------------------------
from PipeSection import * #imports custom PipeSection class
from PipePoint import * #imports custom PipeInOutSection class
#from decimal import Decimal #imports decimal module methods to deal with decimals; documentation: https://docs.python.org/3/library/decimal.html

#high level variables
allPipeSections = [] #list of PipeSection objects where we will track all changes to variables
allPipePoints = [] #list of PipeInOutSection objects that keep track of all flow inputs and outputs

#------------------------------------------VARIABLE INITIALIZATION AND DATA READING FROM FILE---------------------------------------
#initially creates the array of objects from the data in the initial data csv file
def createAllPipeSections():
    file = open("PIPESECTION_FLOW_DATA_IN.csv", "r")
    reading = True
    #read first line of csv file; this line has no real data in it because it is the header to enhance the readability and editability of the csv file
    try:
        str = file.readline()
    except:
        print("Unable to read first line of file " + file.name)
        reading = False
    #read the file and fill the allPipeSections list with PipeSection objects
    while reading == True:
        try:
            list = file.readline().strip().split(",")
            #two for loops that add the correct PipePoint objects to the two-member array in the correct order
            pipePointTempList = []
            for pipePoint in allPipePoints:
                if (pipePoint.getName() == list[0][0:1]):
                    pipePointTempList.append(pipePoint)
                    break
            for pipePoint in allPipePoints:
                if (pipePoint.getName() == list[0][1:2]):
                    pipePointTempList.append(pipePoint)
                    break
            obj = PipeSection(pipePointTempList[0], pipePointTempList[1], float(list[1]), float(list[2]), float(list[3]), float(list[4]))
            allPipeSections.append(obj)
        except: reading = False
    #close the file
    file.close()

#creates all PipePoint objects for the junctions
def createPipePoints():
    file = open("PIPEPOINT_FLOW_DATA_IN.csv", "r")
    reading = True
    #read first line of csv file; this line has no real data in it because it is the header to enhance the readability and editability of the csv file
    try:
        str = file.readline()
    except:
        print("Unable to read first line of file " + file.name)
        reading = False
    #read the file and fill the allPipeSections list with PipeSection objects 
    while reading == True:
        try:
            list = file.readline().strip().split(",")
            allPipePoints.append(PipePoint(list[0], float(list[1])))
        except: reading = False
    #close the file
    file.close()

#-------------------------------------ALL CALCULATION METHODS-----------------------------------------
#calculates head loss given a PipeSection object
def headLossCalc(p):
    qList = p.getFullQHistory()
    qVal = qList[len(qList)-1]
    return (p.getKConst()*qVal*abs(qVal))

#calculates dQ given an array with the names of the loops and the allPipeSections array with all the PipeSection objects
def dQCalc(loop):
    sumNumerator = 0.0
    sumDenominator = 0.0
    for section in loop:
        for sectionObj in allPipeSections:
            if (sectionObj.getPipePoints()[0].getName() in section) and (sectionObj.getPipePoints()[1].getName() in section):
                currentPipeSection = sectionObj
                k = currentPipeSection.getKConst()
                qList = currentPipeSection.getFullQHistory()
                qVal = qList[len(qList)-1]
                sumNumerator = sumNumerator + (k*qVal*abs(qVal))
                sumDenominator = sumDenominator + (k*abs(qVal))
    return (-1.0*(sumNumerator/(2*sumDenominator)))

#defines each flow loop and direction of each flow loop by using the names of each pipe section; returns a 2D array [flow loop][names of pipe sections inside that flow loop]
def loopDefine():
    #for now, just hardcoding the loops for the given problem; in the future, could replace this with a procedural algorithm to automatically detect flow loops given the object data
    loopsArr = [["AB","BE","EI","IH","HA"], ["BC","CF","FE","BE"], ["CD","DG","GF","FC"], ["GJ","JI","IE","EF","FG"]]
    return loopsArr

#output of each loop and all information associated with each pipe section in the loop
def writeLoopInfo(file, loopsArr):
    loopNum = 1
    for loop in loopsArr:
        file.write("LOOP #" + str(loopNum) + ":\n")
        for section in loop:
            for sectionObj in allPipeSections:
                if (sectionObj.getPipePoints()[0].getName() in section) and (sectionObj.getPipePoints()[1].getName() in section):
                    currentSectionObj = sectionObj
            file.write("Section Name (with direction as originally inputted): " + currentSectionObj.getPipePoints()[0].getName() + currentSectionObj.getPipePoints()[1].getName() + " | Friction Factor: " + str(currentSectionObj.getFrictionFactor()) + " | Section Length: " + str(currentSectionObj.getLength()) + " | Pipe Diameter: " + str(currentSectionObj.getDiameter()) + " | Initial Flow Rate Guess " + str(currentSectionObj.getInitialRateGuess()))
            file.write("\n\tQHistory: ")
            file.write(str(currentSectionObj.getFullQHistory()))
            file.write("\n\tHead Loss History: ")
            file.write(str(currentSectionObj.getFullHeadLossHistory()))
            file.write("\n\tdQ History: ")
            file.write(str(currentSectionObj.getDQHistory()))
            file.write("\n")
        loopNum += 1
        file.write("\n")

#writes a section at the end of the file on the mass balances for each Qin or Qout
def writeMassBalanceInfo(file):
    file.write("INPUT/OUTPUT FLOWS / MASS BALANCE:\n")
    for pipePoint in allPipePoints:
        flowSum = 0.0
        flowSumList = []
        if not (pipePoint.getFlow() == 0.0):
            for pipeSection in allPipeSections:
                if (pipePoint.getName() == pipeSection.getPipePoints()[0].getName()): #this means that the PipeSection object starts at the point we're looking at (we don't need to do anything to Q to get the correct flow rate to calculate mass balance)
                    flowSumList.append((pipeSection.getRecentQVal()))
                elif (pipePoint.getName() == pipeSection.getPipePoints()[1].getName()): #this means that the PipeSection object ends at the point we're looking at (we need to do Q*-1 to get the correct flow rate sign) 
                    flowSumList.append(((-1.0)*pipeSection.getRecentQVal()))
        for num in flowSumList:
            flowSum += num
        file.write("Expected flow in or out of system at PipePoint " + pipePoint.getName() + ": " + str(pipePoint.getFlow()) + " | Actual calculated flow: " + str(flowSumList) + " = " + str(flowSum) + "\n")

#creates a .txt log file and outputs all relevant data to it, given the object array of the network with all the data stored in the PipeSection objects
def writeFinalDataToFile(loopsArr):
    create = True
    n = 1
    while create:
        try:
            file = open("DATALOG_OUTPUT_" + str(n) + ".txt", "x")
            create = False
        except: n += 1 
    writeLoopInfo(file, loopsArr)
    writeMassBalanceInfo(file)
    file.close()

#main method call for this class; all method calls within this class will come from this method
#Notes: Q and dQ calculation seems to work just fine now. hL calculation needs to be checked; it doesn't work right now and is not converging. Still need to implement input and output flows (mass balance).
def hardyCrossCalc():
    #define pipe network (the arrangement of flow loops)
    loopsArr = loopDefine()
    #this for loop iterates over the entire pipe network
    for loop in loopsArr:
        #variables for while loop
        hL = 1.0
        dQ = 1.0
        sumHL = 1.0
        #while loop iterates over the loop and solves only the loop
        while ((abs(sumHL) > 0.01) or (abs(dQ) > 0.001)):
            sumHL = 0.0
            for section in loop:
                #figure out which PipeSection object we're considering here
                for sectionObj in allPipeSections:
                    if (sectionObj.getPipePoints()[0].getName() in section) and (sectionObj.getPipePoints()[1].getName() in section):
                        #if statement determines if we're looking at the forward or backward orientation of the section (if the first PipePoint object matches the last letter of the section string, then it's reversed)
                        if (sectionObj.getPipePoints()[0].getName() == section[1:2]):
                            sectionObj.setReversed(True)
                        else: sectionObj.setReversed(False)
                        #calculates the head loss for the section and adds it to the headLossHistory array for that PipeSection object
                        hL = headLossCalc(sectionObj)
                        sectionObj.appendHeadLossHistory(hL)
                        sumHL += hL
            #calculates the dQ for the loop and adds it to the dQHistory array for each PipeSection object in the loop
            dQ = dQCalc(loop)
            for section in loop:
                for sectionObj in allPipeSections:
                    if (sectionObj.getPipePoints()[0].getName() in section) and (sectionObj.getPipePoints()[1].getName() in section):
                        newQVal = (sectionObj.getRecentQVal() + dQ)
                        sectionObj.appendQHistory(newQVal)
                        sectionObj.appendDQHistory(dQ)
    #when all loops are finished, the loop converges, so we can output the convergence values of hL and dQ
    writeFinalDataToFile(loopsArr)

#-------------MAIN METHOD----------------
#main method; executed upon run
def main():
    createPipePoints()
    createAllPipeSections()
    hardyCrossCalc()

#main method call
main()