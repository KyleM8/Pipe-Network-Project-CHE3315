class HardyCross:

    #calculates head loss given a PipeSection object
    def headLossCalc(p):
        qList = p.getFullQHistory()
        qVal = qList[len(qList)-1]
        return (p.getKConst()*qVal*abs(qVal))

    #calculates dQ given a single pipe section
    def dQCalc(pipeSection):
        sumNumerator = 0.0
        sumDenominator = 0.0
        k = pipeSection.getKConst()
        qList = pipeSection.getFullQHistory()
        qVal = qList[len(qList)-1]
        sumNumerator += (k*qVal*abs(qVal))
        sumDenominator += (k*abs(qVal))
        print("QCalc: " + "-1*((" + str(k) + "*" + str(qVal) + "*" + str(abs(qVal)) + ")/(" + str(k) + "*" + str(abs(qVal)) + ")")
        if (qVal == 0): return 0
        else: return (-1*(sumNumerator/(2*sumDenominator)))
    
    #calculates sum of head losses over the entire network
    def calcSumHLNetwork(arr):
        sumHLNetwork = 0.0
        for loop in arr:
            for section in loop:
                try: sumHLNetwork += section.getRecentHLVal()
                except: return 1.0
        return sumHLNetwork

    #defines each flow loop by using the names of each pipe section; returns a 2D array [flow loop][names of pipe sections inside that flow loop]
    def loopDefine():
        #for now, just hardcoding the loops for the given problem; in the future, could replace this with a procedural algorithm to automatically detect flow loops given the object data
        loopsArr = [["AB","BE","EI","IH","HA"], ["BC","CF","FE","BE"], ["CD","DG","GF","FC"], ["GJ","JI","IE","EF","FG"]]
        return loopsArr

    #creates a .txt log file and outputs all relevant data to it, given the object array of the network with all the data stored in the PipeSection objects
    def writeFinalDataToFile(loopsArr, pipeSections):
        create = True
        n = 1
        while create:
            try:
                file = open("DATALOG_OUTPUT_" + str(n) + ".txt", "x")
                create = False
            except: n += 1 
        #output of each loop and all information associated with each pipe section in the loop
        loopNum = 1
        for loop in loopsArr:
            file.write("LOOP #" + str(loopNum) + ":\n")
            for section in loop:
                for sectionObj in pipeSections:
                    if (sectionObj.getName() in section) or (sectionObj.getName() in section[::-1]):
                        currentSectionObj = sectionObj
                file.write("Section Name (with direction): " + section + " | Section Name (without regard to direction): " + currentSectionObj.getName() + " | Friction Factor: " + str(currentSectionObj.getFrictionFactor()) + " | Section Length: " + str(currentSectionObj.getLength()) + " | Pipe Diameter: " + str(currentSectionObj.getDiameter()) + " | Initial Flow Rate Guess " + str(currentSectionObj.getInitialRateGuess()))
                file.write("\n\tQHistory: ")
                file.write(str(currentSectionObj.getFullQHistory()))
                file.write("\n\tHead Loss History: ")
                file.write(str(currentSectionObj.getFullHeadLossHistory()))
                file.write("\n")
            loopNum += 1
            file.write("\n")
        file.close()

    #main method call for this class; all method calls within this class will come from this method
    #NEED TO IMPLEMENT THE IN AND OUT FLOWS STILL!!
    def hardyCrossCalc(pipeSections, pipeInOutSections):
        #define pipe network; the arrangement of flow loops
        loopsArr = HardyCross.loopDefine()
        #this for loop iterates over the entire pipe network
        for loop in loopsArr:
            #variables for while loop
            sumHL = 1.0
            dQ = 1.0
            print("looking at flow loop")
            #this while loop iterates over the loop and solves only the loop
            while ((abs(sumHL) > 0.01) or (abs(dQ) > 0.001)):
                print("internal while loop")
                for section in loop:
                    #figure out which PipeSection object we're considering here
                    for sectionObj in pipeSections:
                        if (sectionObj.getName() in section) or (sectionObj.getName() in section[::-1]):
                            currentSectionObj = sectionObj
                    #if (sectionObj.getName() in section[::-1]):
                    #solve the section
                    print("looking at section " + currentSectionObj.getName() + " for hL")
                    #calculates the head loss for the section and adds it to the headLossHistory array for that PipeSection object
                    sumHL = HardyCross.headLossCalc(currentSectionObj)
                    currentSectionObj.appendHeadLossHistory(sumHL)
                    print("sumHL: " + str(sumHL))
                    #calculates the dQ for the section and adds it to the dQHistory array for that PipeSection object
                    print("looking at section " + currentSectionObj.getName() + " for dQ")
                    dQ = HardyCross.dQCalc(currentSectionObj)
                    currentSectionObj.appendQHistory((currentSectionObj.getRecentQVal() + dQ))
                    currentSectionObj.setDQ(dQ)
                    print("dQ: " + str(dQ))
        #when all loops are finished, the loop converges, so we can output the convergence values of hL and dQ
        HardyCross.writeFinalDataToFile(loopsArr, pipeSections)