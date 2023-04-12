#-------------------------------------IMPORT STATEMENTS AND GLOBAL VARIABLE DECLARATION---------------------------------
import time
from PipeSection import * #imports custom PipeSection class
from PipePoint import * #imports custom PipeInOutSection class

#high level variables
allPipeSections = [] #list of PipeSection objects where we will track all changes to variables
allPipePoints = [] #list of PipeInOutSection objects that keep track of all flow inputs and outputs

#variables for recording execute time
startTime = time.time()

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

#calculates corrections that should be applied to in/out flow points
def calcMassBalCorrections():
    dict = {}
    for pipePoint in allPipePoints:
        flowSum = 0.0
        if not (pipePoint.getFlow() == 0.0):
            for pipeSection in allPipeSections:
                if (pipePoint.getName() == pipeSection.getPipePoints()[0].getName()): #this means that the PipeSection object starts at the point we're looking at (we don't need to do anything to Q to get the correct flow rate to calculate mass balance)
                    flowSum += pipeSection.getRecentQVal()
                elif (pipePoint.getName() == pipeSection.getPipePoints()[1].getName()): #this means that the PipeSection object ends at the point we're looking at (we need to do Q*-1 to get the correct flow rate sign) 
                    flowSum += ((-1.0)*pipeSection.getRecentQVal())
            #check if the flowSum agrees with the correct flows
            diff = pipePoint.getFlow() - flowSum
            correction = 0.0
            if abs(diff) > 0.0001:
                if diff > 0.0:
                    correction = math.sqrt(diff)
                elif diff < 0.0:
                    correction = (-1)*math.pow(((-1)*diff),(10/6)) #only works if the numbers we're dealing with are decimals
            else: correction = 0.0
            dict[pipePoint.getName()] = correction
    return dict

#defines each flow loop and direction of each flow loop by using the names of each pipe section; returns a 2D array [flow loop][names of pipe sections inside that flow loop]
def loopDefine():
    #for now, just hardcoding the loops for the given problem; in the future, could replace this with a procedural algorithm to automatically detect flow loops given the object data
    loopsArr = [["AB","BE","EI","IH","HA"], ["BC","CF","FE","BE"], ["CD","DG","GF","FC"], ["GJ","JI","IE","EF","FG"]]
    return loopsArr

#output of each loop and all information associated with each pipe section in the loop
def writeLoopInfo(file, loopsArr):
    file.write("\nFLOW LOOPS:\n\n")
    loopNum = 1
    for loop in loopsArr:
        file.write("Loop #" + str(loopNum) + ":\n")
        for section in loop:
            for sectionObj in allPipeSections:
                if (sectionObj.getPipePoints()[0].getName() in section) and (sectionObj.getPipePoints()[1].getName() in section):
                    currentSectionObj = sectionObj
            file.write("Section Name (with direction as originally inputted): " + currentSectionObj.getPipePoints()[0].getName() + currentSectionObj.getPipePoints()[1].getName() + " | Friction Factor: " + str(currentSectionObj.getFrictionFactor()) + " | Section Length: " + str(currentSectionObj.getLength()) + " | Pipe Diameter: " + str(currentSectionObj.getDiameter()) + " | Initial Flow Rate Guess " + str(currentSectionObj.getInitialRateGuess()))
            file.write("\n\tFinal flow rate: " + str(currentSectionObj.getRecentQVal()))
            file.write("\n\tQHistory: ")
            file.write(str(currentSectionObj.getFullQHistory()))
            file.write("\n\tHead Loss History: ")
            file.write(str(currentSectionObj.getFullHeadLossHistory()))
            file.write("\n\tdQ History: ")
            file.write(str(currentSectionObj.getDQHistory()))
            file.write("\n\tMass Balance Correction History: ")
            file.write(str(currentSectionObj.getMassBalCorrectionHistory()))
            file.write("\n")
        loopNum += 1
        file.write("\n")

#writes a section at the end of the file on the mass balances for each Qin or Qout
def writeMassBalanceInfo(file):
    file.write("\n\nINPUT/OUTPUT FLOWS / MASS BALANCE:\n")
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
        file.write("Expected flow in or out of system at PipePoint " + pipePoint.getName() + ": " + str(pipePoint.getFlow()) + "\nActual calculated flow in or out: " + str(flowSumList) + " = " + str(flowSum) + "\n\n")

#creates a .txt log file and outputs all relevant data to it, given the object array of the network with all the data stored in the PipeSection objects
def writeFinalDataToFile(loopsArr, counter):
    create = True
    n = 1
    while create:
        try:
            file = open("DATALOG_OUTPUT_" + str(n) + ".txt", "x")
            create = False
        except: n += 1 
    file.write("Units are in m and m^3/s.\n\n")
    writeLoopInfo(file, loopsArr)
    writeMassBalanceInfo(file)
    file.write("\n\nIterations to converge within limits: " + str(counter) + "\nNote: more iterations are possible to obtain more precision, and tolerances are changeable depending on the precision required. For this project statement, the current precision is more than acceptable.")
    endTime = time.time()
    file.write("\nProgram time to execute: " + str(((endTime - startTime)*10**3)) + " ms") #NEED A PROGRAM TIME NUMBER!!
    file.close()

#overall logic for when to stop calculating the number
def stillCalculating(loopsArr, counter):
    if (counter < 4): return True
    #criteria to return false: abs(sumHL) for each loop is < 0.01; abs(dQ) for each pipe section is < 0.001; abs() of mass balance correction is < 0.001 for each pipe section
    sumHL = 0.0
    for loop in loopsArr:
        sumHL = 0.0
        for section in loop:
            for sectionObj in allPipeSections:
                if (sectionObj.getPipePoints()[0].getName() in section) and (sectionObj.getPipePoints()[1].getName() in section):
                    sumHL += sectionObj.getRecentHLVal()
        if (abs(sumHL) > 0.01): return True
    for loop in loopsArr:
        for section in loop:
            for sectionObj in allPipeSections:
                if (sectionObj.getPipePoints()[0].getName() in section) and (sectionObj.getPipePoints()[1].getName() in section):
                    dQ = sectionObj.getRecentQVal()
                    mBCorr = sectionObj.getRecentMassBalCorrection()
                    if ((abs(dQ) > 0.001) and (abs(mBCorr) > 0.00001)): return True
    return False

#main method call for this class; all method calls within this class will come from this method
def hardyCrossCalc():
    #define pipe network (the arrangement of flow loops)
    loopsArr = loopDefine()
    counter = 1
    while stillCalculating(loopsArr, counter):
        #this for loop iterates over each loop
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
        #calculates an additional correction based on known mass balance values and applies it
        massBalDict = calcMassBalCorrections()
        for pipePoint in allPipePoints:
            if (pipePoint.getName() in massBalDict):
                correction = massBalDict.get(pipePoint.getName())
                for sectionObj in allPipeSections:
                    if (pipePoint.getName() == sectionObj.getPipePoints()[0].getName()): #this means that the PipeSection object starts at the point we're looking at (we don't need to do anything to Q to get the correct flow rate to calculate mass balance)
                        newQVal = (sectionObj.getRecentQVal() + correction)
                        sectionObj.appendQHistory(newQVal)
                        sectionObj.appendMassBalCorrectionHistory(correction)
                    elif (pipePoint.getName() == sectionObj.getPipePoints()[1].getName()): #this means that the PipeSection object ends at the point we're looking at (we need to do Q*-1 to get the correct flow rate sign) 
                        newQVal = (sectionObj.getRecentQVal() + ((-1)*correction))
                        sectionObj.appendQHistory(newQVal)
                        sectionObj.appendMassBalCorrectionHistory(((-1)*correction))
        counter += 1
    #when all loops are finished, the loop converges, so we can output the convergence values of hL and dQ
    writeFinalDataToFile(loopsArr, counter)

#-------------MAIN METHOD AND TIMING----------------
#main method; executed upon run
def main():
    startTime = time.time()
    createPipePoints()
    createAllPipeSections()
    hardyCrossCalc()

#main method call
main()