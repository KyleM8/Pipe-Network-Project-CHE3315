from PipeSection import * #imports custom PipeSection class
from PipeInOutSection import * #imports custom PipeInOutSection class
from HardyCross import * #imports methods that implement the HardyCross calculation 
#from decimal import * #imports decimal module methods to deal with decimals; documentation: https://docs.python.org/3/library/decimal.html

#class-level variables
pipeSections = [] #list of PipeSection objects where we will track all changes to variables
pipeInOutSections = [] #list of PipeInOutSection objects that keep track of all flow inputs and outputs

#initially creates the array of objects from the data in the initial data csv file
def intermediateFlowDataFromFile():
    file = open("INTERMEDIATE_FLOW_DATA_IN.csv", "r")
    reading = True
    #read first line of csv file; this line has no real data in it because it is the header to enhance the readability and editability of the csv file
    try:
        str = file.readline()
    except:
        print("Unable to read first line of file " + file.name)
        reading = False
    #read the file and fill the pipeSections list with PipeSection objects 
    while reading == True:
        try:
            list = file.readline().strip().split(",")
            pipeSections.append(PipeSection(list[0], float(list[1]), float(list[2]), float(list[3]), float(list[4])))
        except:
            print("Finished reading file " + file.name)
            reading = False
    #close the file
    file.close()

def inOutFlowDataFromFile():
    file = open("INPUT_OUTPUT_FLOW_DATA_IN.csv", "r")
    reading = True
    #read first line of csv file; this line has no real data in it because it is the header to enhance the readability and editability of the csv file
    try:
        str = file.readline()
    except:
        print("Unable to read first line of file " + file.name)
        reading = False
    #read the file and fill the pipeSections list with PipeSection objects 
    while reading == True:
        try:
            list = file.readline().strip().split(",")
            pipeInOutSections.append(PipeInOutSection(list[0], float(list[1])))
        except:
            print("Finished reading file " + file.name)
            reading = False
    #close the file
    file.close()

def debug_printPipeSectionsList():
    for p in pipeSections:
        p.printData()
        print("")
    for p in pipeInOutSections:
        p.printData()
        print("")

#main method; executed upon run
def main():
    intermediateFlowDataFromFile()
    inOutFlowDataFromFile()
    debug_printPipeSectionsList() #only here for debugging purposes
    HardyCross.hardyCrossCalc(pipeSections, pipeInOutSections)

#main method call
main()