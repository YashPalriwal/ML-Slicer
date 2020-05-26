from subprocess import call

class MyCFG():

    def __init__(self):
        self.nodes = dict()
        self.dotGraph = ""
        self.parentlist = {}
        self.childlist = {}

    def addNode(self, node):
        self.nodes[node.id] = node

    def connect(self, a, b):
        self.nodes[a].addChild(b)
        self.nodes[b].setParent(a)

    def printPretty(self):
        for nodeId in self.nodes:
            #print("nodeId ", " --> ", nodeId)
            self.childlist[nodeId] = []

            for i in self.nodes[nodeId].next:
                self.childlist[nodeId].append(i)
                # print(i, "\t", end='')
            # print("parents : ", end='')
            self.parentlist[nodeId] = []
            for i in self.nodes[nodeId].parent:
                #print("nodes[",nodeId,"].parent = ", self.nodes[nodeId].parent)
                # tmp.append(i)
                #print("appending i = ",i)
                self.parentlist[nodeId].append(i)
            # print("")
        # print("Parents CFG ---->>>>  ",self.parentlist)
        # print("childeren CFG ----->>>>",self.childlist)
        return self.parentlist,self.childlist


    def dotToPng(self, dotString, filename):
        file = open(filename, 'w')
        file.write(dotString)
        file.close()

        call(["dot", "-Tpng", "-o", filename + ".png", filename])
        call(["eog", filename + ".png"])
