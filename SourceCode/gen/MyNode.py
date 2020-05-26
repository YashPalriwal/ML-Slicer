class MyNode():

    def __init__(self, id, ctx=None):
        self.id = id
        self.ctx = ctx
        self.next = set()
        self.parent = set()
        #self.domSet = set()
        #self.sDomSet = set()
        #self.iDom = None
        self.DFSet = set()
        self.levelFromEntryNode = -1
        self.phiNode = dict()           # format would be { 'x' : [['x'], ['x', 'x', 'x']] }
        self.variableSet = set()
        self.variableLHS = set()
        self.variableRHS = set()
        #self.versionedPhiNode = dict()  # format {'x': [['x1'], [{15: 'x2', 14: 'x3', 16: 'x4'}]]}
        #self.versionedRHS = dict()
        #self.versionedLHS = dict()
        #self.destructedPhi = dict()
        self.branching = dict()
        self.stringSsa = ""
        #self.oldString = ""
        #self.color = "black"
        #self.visited = 0
        #self.condtionalNode = False

    def addChild(self, node):
        self.next.add(node)

    def setParent(self, parent):
        self.parent.add(parent)


    def printPretty(self):
        print("------------------------------")
        #print("Context = ", self.ctx.getText())
        print("id = ", self.id)
        print("next : ", self.next)
        print("parent : ", self.parent)

        #print("domSet : ", self.domSet)
        #print("sDomSet : ", self.sDomSet)
        #print("iDom : ", self.iDom)
        #print("DFSet : ", self.DFSet)
        #print("phiNode : ", self.phiNode)

        #print("variableSet : ", self.variableSet)

        #print("variableLHS : ", self.variableLHS)
        #print("variableRHS : ", self.variableRHS)
        #print("versionedPhiNode : ", self.versionedPhiNode)
        #print("versionedRHS : ", self.versionedRHS)
        #print("versionedLHS : ", self.versionedLHS)
        #print("destructedPhi : ", self.destructedPhi)
        #print("branching : ", self.branching)

        #print("---oldString : ", self.oldString)
        #print("---stringSsa : ", self.stringSsa)
        #print("--- Color : ", self.color)
        #print("--- Visited : ", self.visited)
        #print("--- Condtional Node: ", self.condtionalNode)
        
        
        
