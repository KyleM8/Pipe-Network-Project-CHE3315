#-------------------------------------IMPORT STATEMENTS AND GLOBAL VARIABLE DECLARATION---------------------------------
import time
import numpy as np
import platform
from PipeSection import * #imports custom PipeSection class
from PipePoint import * #imports custom PipePoint class

#high level variables
allPipeSections = [] #list of PipeSection objects where we will track all changes to variables
allPipePoints = [] #list of PipeInOutSection objects that keep track of all flow inputs and outputs

#variables for recording execute time
startTime = time.time()

#variable for iteration limit
#before an active culling system for the arrays was implemented, the code would terminate with exit code -1 somewhere between 2000 and 5000 iterations because the arrays became too much for the memory to handle (at least on my 8GB RAM laptop)
#before this system was implemented, using Task Manager showed that each iteration required about 3MB of RAM, which points to this process being absurdly inefficient (was not expecting to need this many iterations when writing the code this way, and kept having to add more RAM-heavy arrays and variables)
#if we did actually need every single value of the array for some reason, the efficiency issue could be fixed by writing the arrays into working .json files instead and just keeping a record of the index we're working with (can much more easily and efficiently store a long integer in RAM rather than an array of a few thousand elements)
#however, as a simple fix to the efficiency issue, the array culling system is more than enough optimization, since with this many iterations, the most recent value is really the only one needed
outerIterationLimit = 10
innerIterationLimit = 10

#---------------------------------------VARIABLE INITIALIZATION AND DATA READING FROM FILE---------------------------------------
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

#----------------------------------OUTPUT FILE WRITING----------------------------------------------
#output of each loop and information associated with each pipe section in the loop
def writeLoopInfo(file, loopsArr):
    file.write("\nFLOW LOOPS:\n\n")
    loopNum = 1
    for loop in loopsArr:
        file.write("Loop #" + str(loopNum) + ":\n")
        sumHL = 0.0
        for section in loop:
            for sectionObj in allPipeSections:
                if (sectionObj.getPipePoints()[0].getName() in section) and (sectionObj.getPipePoints()[1].getName() in section):
                    currentSectionObj = sectionObj
            file.write("Section Name (with direction as originally inputted): " + currentSectionObj.getName() + " | Friction Factor: " + str(currentSectionObj.getFrictionFactor()) + " | Section Length: " + str(currentSectionObj.getLength()) + " | Pipe Diameter: " + str(currentSectionObj.getDiameter()) + " | Initial Flow Rate Guess " + str(currentSectionObj.getInitialRateGuess()))
            # file.write("\n\tQHistory: ")
            # file.write(str(currentSectionObj.getFullQHistory()))
            file.write("\n\tFinal flow rate: " + str(currentSectionObj.getRecentQVal()))
            # file.write("\n\tHead Loss History: ")
            # file.write(str(currentSectionObj.getFullHeadLossHistory()))
            file.write("\n\tLast head loss value: " + str(currentSectionObj.getRecentHLVal()))
            sumHL += currentSectionObj.getRecentHLVal()
            # file.write("\n\tdQ History: ")
            # file.write(str(currentSectionObj.getDQHistory()))
            file.write("\n\tLast dQ value: " + str(currentSectionObj.getRecentDQ()))
            # file.write("\n\tMass Balance Correction History: ")
            # file.write(str(currentSectionObj.getMassBalCorrectionHistory()))
            file.write("\n\tLast mass balance correction value: " + str(currentSectionObj.getRecentMassBalCorrection()))
            file.write("\n")
        file.write("Total head loss value for loop: " + str(sumHL) + "\n")
        loopNum += 1
        file.write("\n")

#writes a section at the end of the file on the mass balances for each Qin or Qout
def writeMassBalanceInfo(file):
    file.write("\n\nINPUT/OUTPUT FLOWS / MASS BALANCE:\n")
    for pipePoint in allPipePoints:
        flowSum = 0.0
        flowSumList = []
        for pipeSection in allPipeSections:
            if (pipePoint.getName() == pipeSection.getPipePoints()[0].getName()): #this means that the PipeSection object starts at the point we're looking at (we don't need to do anything to Q to get the correct flow rate to calculate mass balance)
                flowSumList.append((pipeSection.getRecentQVal()))
            elif (pipePoint.getName() == pipeSection.getPipePoints()[1].getName()): #this means that the PipeSection object ends at the point we're looking at (we need to do Q*-1 to get the correct flow rate sign) 
                flowSumList.append(((-1.0)*pipeSection.getRecentQVal()))
        for num in flowSumList:
            flowSum += num
        file.write("Expected flow in or out of system at PipePoint " + pipePoint.getName() + ": " + str(pipePoint.getFlow()) + "\nActual calculated flow in or out: " + str(flowSumList) + " = " + str(flowSum) + "\n\n")

#creates a .txt log file and outputs all relevant data to it, given the object array of the network with all the data stored in the PipeSection objects
def writeFinalDataToFile(loopsArr, outerCounter, innerCounter):
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
    file.write("\n\nFINAL FLOW NUMBERS:\n")
    for sectionObj in allPipeSections:
        file.write("Q for section " + sectionObj.getName() + ": " + str(sectionObj.getRecentQVal()) + "\n")
    file.write("\n\nLimited to " + str(outerIterationLimit) + " outer iterations. Outer iterations run: " + str(outerCounter) + ".\nLimited to " + str(innerIterationLimit) + " inner iterations. Inner iterations run: " + str(innerCounter) + ".")
    file.write("\nHardware info: OS: " + platform.system() + " | CPU: " + platform.processor())
    endTime = time.time()
    file.write("\nProgram time to execute: " + str(endTime-startTime) + " sec = " + str((endTime-startTime)/60.0) + " mins") #str(((endTime - startTime)*10**3)) + " ms"
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

#calculates corrections that should be applied to pipe sections
def calcMassBalCorrections():
    dict = {}
    for pipePoint in allPipePoints:
        flowSum = 0.0
        for pipeSection in allPipeSections:
            if (pipePoint.getName() == pipeSection.getPipePoints()[0].getName()): #this means that the PipeSection object starts at the point we're looking at (we don't need to do anything to Q to get the correct flow rate to calculate mass balance)
                flowSum += pipeSection.getRecentQVal()
            elif (pipePoint.getName() == pipeSection.getPipePoints()[1].getName()): #this means that the PipeSection object ends at the point we're looking at (we need to do Q*-1 to get the correct flow rate sign) 
                flowSum += ((-1.0)*pipeSection.getRecentQVal())
        #check if the flowSum agrees with the correct flows
        if (pipePoint.getFlow() > 0) and (flowSum > 0): diff = pipePoint.getFlow() - flowSum
        else: diff = abs(pipePoint.getFlow()) - abs(flowSum)
        correction = 0.0
        if (abs(diff) > 0.000001 and abs(diff) < 1.0):
            if diff > 0.0:
                correction = np.power(diff,(1.5)) #only works if the numbers we're dealing with are decimals
            elif diff < 0.0:
                correction = (-1)*np.power(abs(diff),(1.5)) #only works if the numbers we're dealing with are decimals
        else: correction = 0.0
        numSections = 0
        for pP in allPipePoints:
            for pipeSection in allPipeSections:
                if (pP.getName() in pipeSection.getName()): numSections += 1
        dict[pipePoint.getName()] = correction/numSections
    newDict = {}
    for pipeSection in allPipeSections:
        newDict[pipeSection.getName()] = ((dict.get(pipeSection.getPipePoints()[0].getName()) + (dict.get(pipeSection.getPipePoints()[1].getName())))/2.0)
    #print("newDict: " + str(newDict))
    return newDict

#defines each flow loop and direction of each flow loop by using the names of each pipe section; returns a 2D array [flow loop][names of pipe sections inside that flow loop]
def loopDefine():
    #for now, just hardcoding the loops for the given problem; in the future, could replace this with a procedural algorithm to automatically detect flow loops given the object data
    loopsArr = [["AB","BE","EI","IH","HA"], ["BC","CF","FE","BE"], ["CD","DG","GF","FC"], ["GJ","JI","IE","EF","FG"]]
    return loopsArr

#check if the expected flow rates are calculated correctly by cross-checking with the given mass balance information; returns true if flows are correct, returns false if more calculation is necessary
def massBalanceValid():
    boolList = []
    for pipePoint in allPipePoints:
        flowSum = 0.0
        for pipeSection in allPipeSections:
            if (pipePoint.getName() == pipeSection.getPipePoints()[0].getName()): #this means that the PipeSection object starts at the point we're looking at (we don't need to do anything to Q to get the correct flow rate to calculate mass balance)
                flowSum += pipeSection.getRecentQVal()
            elif (pipePoint.getName() == pipeSection.getPipePoints()[1].getName()): #this means that the PipeSection object ends at the point we're looking at (we need to do Q*-1 to get the correct flow rate sign) 
                flowSum += ((-1.0)*pipeSection.getRecentQVal())
        #check if the flowSum agrees with the correct flows
        diff = abs(pipePoint.getFlow()) - abs(flowSum)
        if (abs(diff) < 0.001):
            boolList.append(True) #adds a true value if the flows match the mass balance, false if the flows do not match the mass balance
        else: boolList.append(False)
    #print(boolList)
    for bool in boolList:
        if bool == False:
            return False
    return True

#culls arrays to ensure that the calculation is possible (thousands of iterations of adding to an array is a huge waste of resources and slows down the process quite a bit)
def cullArrays():
    for section in allPipeSections: #cull arrays for Q history, head loss history, dQ history, mass balance correction history
        hLArr = section.getFullHeadLossHistory()
        qArr = section.getFullQHistory()
        dQArr = section.getDQHistory()
        massBalArr = section.getMassBalCorrectionHistory()
        if len(hLArr) > 10: section.cullHLArr()
        if len(qArr) > 10: section.cullQArr()
        if len(dQArr) > 10: section.cullDQArr()
        if len(massBalArr) > 10: section.cullMassBalCorrArr()

#overall logic for when to stop calculating the number
#criteria to return false: abs(sumHL) for each loop is < 0.01; abs(dQ) for each pipe section is < 0.001; abs() of mass balance correction is < 0.001 for each pipe section, and the given mass balances are valid
#(currently a little redundant, as it seems to never return false even though the numbers converge to reasonable values; this is why we have an iteration limit implemented)
def stillCalculating(loopsArr, counter):
    if (counter < 4): return True
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
                    if ((abs(dQ) > 0.001) and (abs(mBCorr) > 0.0001)): return True
    if massBalanceValid() == False: return True 
    return False

#returns true if all sums of head losses for each loop are convergent, returns false otherwise
def checkAllSumHL(loopsArr):
    for loop in loopsArr:
        sumHL = 0.0
        for section in loop:
            for sectionObj in allPipeSections:
                if (sectionObj.getPipePoints()[0].getName() in section) and (sectionObj.getPipePoints()[1].getName() in section):
                    sumHL += sectionObj.getRecentHLVal()
        if abs(sumHL) > 0.01: return False
    return True

#returns true if all dQ values for every pipe section are convergent, returns false otherwise
def checkAllDQ(loopsArr):
    for loop in loopsArr:
        for section in loop:
            for sectionObj in allPipeSections:
                if (sectionObj.getPipePoints()[0].getName() in section) and (sectionObj.getPipePoints()[1].getName() in section):
                    if abs(sectionObj.getRecentQVal()) > 0.001: return False
    return True

#given an array of names of sections in a loop and a pipeSection object, return if the pipe section is in the loop
def inLoop(loop, pipeSection):
    for string in loop:
        if pipeSection.getName() == string: return True
    return False

#prints bass balance info for debug purposes
def debug_printMassBals():
    for pipePoint in allPipePoints:
        flowSum = 0.0
        flowSumList = []
        for pipeSection in allPipeSections:
            if (pipePoint.getName() == pipeSection.getPipePoints()[0].getName()): #this means that the PipeSection object starts at the point we're looking at (we don't need to do anything to Q to get the correct flow rate to calculate mass balance)
                flowSumList.append((pipeSection.getRecentQVal()))
            elif (pipePoint.getName() == pipeSection.getPipePoints()[1].getName()): #this means that the PipeSection object ends at the point we're looking at (we need to do Q*-1 to get the correct flow rate sign) 
                flowSumList.append(((-1.0)*pipeSection.getRecentQVal()))
        for num in flowSumList:
            flowSum += num
        print("Expected flow in or out of system at PipePoint " + pipePoint.getName() + ": " + str(pipePoint.getFlow()) + "\nActual calculated flow in or out: " + str(flowSumList) + " = " + str(flowSum) + "\n\n")

#main method call for the calculation implementation; all method calls for calculation come from this method
def hardyCrossCalc():
    #define pipe network (the arrangement of flow loops)
    loopsArr = loopDefine()
    counter = 1
    while stillCalculating(loopsArr, counter):

        #this loop ensures that we iterate over the entire flow loop and solve it correctly before moving on to the next "outer" iteration
        innerCounter2 = 1
        while (not checkAllSumHL(loopsArr) and not checkAllDQ(loopsArr) and not massBalanceValid()) or innerCounter2 == 1:

            hL = 0.0
            dQ = 1.0
            sumHL = 1.0
            correction = 1.0
            while ((abs(sumHL) > 0.01) or (abs(dQ) > 0.001)):

                for sectionObj in allPipeSections:
                    massBalDict = calcMassBalCorrections() #calculates mass balance corrections
                    #applies mass bal correction
                    correction = massBalDict.get(sectionObj.getName())
                    newQVal = sectionObj.getRecentQVal() + correction
                    sectionObj.appendQHistory(newQVal)
                    sectionObj.appendMassBalCorrectionHistory(correction)
                    print("applying mbal correction of " + str(correction) + " to " + sectionObj.getName() + " for new Q of " + str(newQVal))

                for loop in loopsArr:

                    
                    for section in loop:
                        for sectionObj in allPipeSections:
                            dQ = dQCalc(loop) #calculates dQ for the loop
                            if (sectionObj.getPipePoints()[0].getName() in section) and (sectionObj.getPipePoints()[1].getName() in section):
                                #applies dQ
                                newQVal = (sectionObj.getRecentQVal() + dQ)
                                sectionObj.appendQHistory(newQVal)
                                sectionObj.appendDQHistory(dQ)
                                print("applying dQ of " + str(dQ) + " to " + sectionObj.getName() + " for new Q of " + str(newQVal))


                        #calculates the head loss for each element in the loop and calculates sum of the head losses for the loop
                        sumHL = 0.0
                        for section in loop:
                            #figure out which PipeSection object we're considering here
                            for sectionObj in allPipeSections:
                                if (sectionObj.getPipePoints()[0].getName() in section) and (sectionObj.getPipePoints()[1].getName() in section):
                                    #calculates the head loss for the section and adds it to the headLossHistory array for that PipeSection object
                                    hL = headLossCalc(sectionObj)
                                    sectionObj.appendHeadLossHistory(hL)
                                    sumHL += hL
                        print("sumHL for loop " + str(loop) + " is " + str(sumHL))
                debug_printMassBals()        

            innerCounter2 += 1
            
            cullArrays()
            debug_printMassBals()
            print("INNER ITERATION: " + str(innerCounter2))
            # if (innerCounter1 >= innerIterationLimit): break
            # innerCounter1 += 1
            # #time.sleep(1)
            input("Waiting for keypress...")
            
        cullArrays()
        debug_printMassBals()
        print("OUTER ITERATION: " + str(counter))
        if counter >= outerIterationLimit: break
        counter += 1
        #time.sleep(1)
        #input("Waiting for keypress...")
        
    #when all loops are finished, the loop converges, so we can output the convergence values of hL and dQ
    writeFinalDataToFile(loopsArr, counter, innerCounter2)

#-------------MAIN METHOD AND TIMING----------------
#main method; executed upon run
def main():
    createPipePoints()
    createAllPipeSections()
    hardyCrossCalc()

#main method call
main()