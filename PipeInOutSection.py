class PipeInOutSection:

    def __init__(self, n, fR):
        #identifying information for each pipe section given in problem statement
        self.name = n #string to identify the pipe section, e.g. "A"
        self.flowRate = fR #flow rate in or out (positive for in, negative for out)

    def printData(self):
        print("name: " + self.name)
        print("flow rate: " + str(self.flowRate))