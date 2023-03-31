class HardyCross:

    #calculates head loss given a PipeSection object
    def headLossCalc(p):
        qList = p.getQHistory()
        qVal = qList[len(qList)-1]
        return p.getKConst()*qVal*abs(qVal)

    #calculates dQ given an array of pipe sections (containing the PipeSection objects for all the sections in a certain flow loop)
    def dQCalc(pArr):
        sumNumerator = 0.0
        sumDenominator = 0.0
        for p in pArr:
            k = p.getKConst()
            qList = p.getQHistory()
            qVal = qList[len(qList)-1]
            sumNumerator += (k*qVal*abs(qVal))
            sumDenominator += (k*abs(qVal))
        return (-1*(sumNumerator/(2*sumDenominator)))
    
    #defines each flow loop by using the names of each pipe section; returns a 2D array [flow loop][names of pipe sections inside that flow loop]
    def loopDefine(pS):
        #for now, just hardcoding the loops for the given problem; in the future, could replace this with a procedural algorithm to automatically detect flow loops given the object data
        arr = [["AB","BE","EI","IH","HA"], ["BC","CF","FE","EB"], ["CD","DG","GF","FC"], ["GJ","JI","IE","EF","FG"]]
        #array to put PipeSection objects into
        objArr = [[]]
        #counters
        x = 0
        y = 0
        for i in arr:
            for j in i:
                for section in pS:
                    if (section.getName() == j):
                        objArr[x][y] = section
                y += 1
            x += 1
        return objArr

    #creates a .txt log file and outputs all relevant data to it, given the object array of the network with all the data stored in the PipeSection objects
    def writeFinalDataToFile(arr):
        create = True
        file
        n = 1
        while create:
            try:
                file = open("DATALOG_OUTPUT_" + str(n), "x")
                create = False
            except: n += 1
        file.write("text")
        #items to output in log file:
            #as reference and to ensure we're not getting something small wrong: a section with the pipe section name, friction factor, length, diameter, and initial flow rate guess for each pipe section
            #entirety of qHistory, headLossHistory, and flowRateHistory arrays for each pipe section; loop definitions; 

    #main method call for this class; all method calls within this class will come from this method
    #NEED TO IMPLEMENT THE IN AND OUT FLOWS!!
    def hardyCrossCalc(pipeSections, pipeInOutSections):
        #define pipe network; the arrangement of flow loops
        network = loopDefine(pipeSections)
        #outer while loop variables
        sumHLOuter = 0.0
        dQ= 0.0
        #this while loop iterates over the entire pipe network
        while (abs(sumHLOuter) > 0.01) or (abs(dQ) > 0.001):
            for loop in network:
                #inner while loop variables
                sumHLInner = 0.0
                #this while loop iterates over the loop and solves only the loop
                while (abs(sumHLInner) > 0.01) or (abs(dQ) > 0.001):
                    for section in loop:
                        section.appendHeadLossHistory(headLossCalc(section)) #calculates the head loss for the section and adds it to the headLossHistory array for that PipeSection object
                dQ = dQCalc(loop)
                for section in loop:
                    section.appendQHistory(section.getRecentQVal() + dQ)
                
        #when all loops are finished, the loop converges, so we can output the convergence values of hL and dQ
        writeFinalDataToFile(network)