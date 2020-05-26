
import queue

from gen.PlSqlVisitor import PlSqlVisitor

from MyHelper import MyHelper

time = 0

class MyUtility():


    def __init__(self, helper):
        self.helper = helper


    def generateDomSet(self, cfg):
        nodeIdSet = set()
        for nodeId in cfg.nodes:        # taking all the node ID's in a set
            nodeIdSet.add(nodeId)
        cfg.nodes[0].domSet.add(0)
        prev = dict()
        prev[0] = {0}
        for nodeId in nodeIdSet:        # initialising the dominator set of all nodes to set of all nodes, except the entry node
            if nodeId == 0:
                continue
            cfg.nodes[nodeId].domSet = set(nodeIdSet)
        while True:
            for i in nodeIdSet:
                prev[i] = set(cfg.nodes[i].domSet)
            self.updateDomSet(cfg, nodeIdSet)
            if not(self.isDomSetChanged(cfg, prev, nodeIdSet)):
                break

    def updateDomSet(self, cfg, nodeIdSet):
        for nodeId in nodeIdSet:
            if nodeId == 0:
                continue
            else:
                res = set(nodeIdSet)
                for parent in cfg.nodes[nodeId].parent:
                    res = res.intersection(cfg.nodes[parent].domSet)
                res.add(nodeId)
                cfg.nodes[nodeId].domSet = res

    def isDomSetChanged(self, cfg, prev, nodeIdSet):
        res = False
        for nodeId in nodeIdSet:
            if prev[nodeId].intersection(cfg.nodes[nodeId].domSet) != prev[nodeId]:
                res = True
                break
        return res

    def generateSDomSet(self, cfg):
        for nodeId in cfg.nodes:
            res = set(cfg.nodes[nodeId].domSet)
            self.removeFromSet(res, nodeId)
            cfg.nodes[nodeId].sDomSet = res

    def removeFromSet(self, targetSet, value):
        if value in targetSet:
            targetSet.remove(value)

    def generatIDom(self, cfg):
        self.BFS(cfg)
        for nodeId in cfg.nodes:
            res = 9999999
            for dom in cfg.nodes[nodeId].sDomSet:
                if abs(cfg.nodes[nodeId].levelFromEntryNode - cfg.nodes[dom].levelFromEntryNode) < res:
                    res = abs(cfg.nodes[nodeId].levelFromEntryNode - cfg.nodes[dom].levelFromEntryNode)
                    cfg.nodes[nodeId].iDom = dom

    def BFS(self, cfg):
        q = queue.Queue()
        q.put(0)
        cfg.nodes[0].levelFromEntryNode = 0
        while not q.empty():
            node = q.get()
            for nodeId in cfg.nodes[node].next:
                if cfg.nodes[nodeId].levelFromEntryNode == -1:
                    q.put(nodeId)
                    cfg.nodes[nodeId].levelFromEntryNode = cfg.nodes[node].levelFromEntryNode + 1

    def generateDFSet(self, cfg):
        for nodeId in cfg.nodes:
            for parent in cfg.nodes[nodeId].parent:
                temp = parent
                while temp != cfg.nodes[nodeId].iDom:
                    cfg.nodes[temp].DFSet.add(nodeId)
                    temp = cfg.nodes[temp].iDom

    def generateVariableSet(self, cfg):
        res = set()
        for nodeId in cfg.nodes:
            cfg.nodes[nodeId].variableSet = set(self.helper.getVariableSet(cfg.nodes[nodeId].ctx))#, nodeId) )   #TODO: remove nodeId
            res = res.union(cfg.nodes[nodeId].variableSet)
            cfg.nodes[nodeId].variableRHS = self.helper.generateRHS(cfg.nodes[nodeId].ctx)#, nodeId)   #TODO: remove nodeId
            #print(cfg.nodes[nodeId].variableRHS)
            cfg.nodes[nodeId].variableLHS = self.helper.generateLHS(cfg.nodes[nodeId].ctx)#, nodeId)   #TODO: remove nodeId

        return res


    def insertPhiNode(self, cfg):
        variables = self.generateVariableSet(cfg)
        for var in variables:
            hasAlready = set()
            everOnWorklist = set()
            workList = set()
            for nodeId in cfg.nodes:
                if self.helper.isAssignEq(cfg.nodes[nodeId].ctx) and (var in cfg.nodes[nodeId].variableLHS): #and var == self.helper.assignedVar(cfg.nodes[nodeId].ctx): #TODO change : remove nodeId from parameter, USE "LHS SET" INSTEAD OF "assignedVar"
                    everOnWorklist.add(nodeId)# = everOnWorklist.union(set(nodeId))
                    workList.add(nodeId)# = workList.union(set(nodeId))
            while not len(workList) == 0:
                x = workList.pop()
                for y in cfg.nodes[x].DFSet:
                    if not(y in hasAlready):
                        temp = [var]*len(cfg.nodes[y].parent)
                        cfg.nodes[y].phiNode[var] = [[var], temp]
                    hasAlready.add(y)# = hasAlready.union(set(y))
                    if not(y in everOnWorklist):
                        everOnWorklist.add(y)# = everOnWorklist.union(set(y))
                        workList.add(y)# = workList.union(set(y))


    def initialiseVersinosedPhiNode(self, cfg):
        for nodeId in cfg.nodes:
            temp = dict()
            for parent in cfg.nodes[nodeId].parent:
                temp[parent] = ''
            for phi in cfg.nodes[nodeId].phiNode:
                cfg.nodes[nodeId].versionedPhiNode[phi] = [[],[dict(temp)]]


    def getVariableDict(self, cfg):
        res = set()
        for nodeId in cfg.nodes:
            res = res.union(cfg.nodes[nodeId].variableSet)
        resDict = dict()

        for var in res:
            resDict[var] = 0
        return resDict

    def getStackDict(self, cfg):
        res = set()
        for nodeId in cfg.nodes:
            res = res.union(cfg.nodes[nodeId].variableSet)
        resDict = dict()
        for var in res:
            resDict[var] = [0]
        return resDict

    def versioniseVariable(self, cfg):
        stacks = dict()#self.getStackDict(cfg)
        counters = self.getVariableDict(cfg)
        visited = dict()
        for nodeId in cfg.nodes:
            visited[nodeId] = False
        self.rename(cfg, 0, stacks, counters, visited)

    def genName(self, cfg, node, stacks, counters, var, isPhiNode):
        i = counters[var]
        if isPhiNode:
            cfg.nodes[node].versionedPhiNode[var][0].append(var + str(i))
        else:
            cfg.nodes[node].versionedLHS[var] = var + str(i)
        if var in stacks.keys():
            stacks[var].append(i)
        else:
            stacks[var] = [i]
        counters[var] = i + 1


    def rename(self, cfg, node, stacks, counters, visited):
        if not visited[node]:
            visited[node] = True
            for phi in cfg.nodes[node].phiNode:
                self.genName(cfg, node, stacks, counters, phi, True)
            for var in cfg.nodes[node].variableSet:
                if not(var in stacks.keys()):
                    stacks[var] = [0]
                    counters[var] = 1
                if var in cfg.nodes[node].variableRHS:
                    cfg.nodes[node].versionedRHS[var] = var + str(stacks[var][len(stacks[var]) - 1])
                if var in cfg.nodes[node].variableLHS:
                    self.genName(cfg, node, stacks, counters, var, False)
            for succ in cfg.nodes[node].next:
                j = node
                for phi in cfg.nodes[succ].phiNode.keys():
                    # print("@@@@@@@ stack ", stacks)
                    # print("@@@@@@@ counters ", counters)
                    # print("@@@@@@@ versionedPhiNode ", cfg.nodes[succ].versionedPhiNode)
                    cfg.nodes[succ].versionedPhiNode[phi][1][0][j] = phi + str(stacks[phi][len(stacks[phi]) - 1])

            for succ in cfg.nodes[node].next:
                self.rename(cfg, succ, stacks, counters, visited)

            for var in cfg.nodes[node].variableLHS:
                stacks[var].pop()

            for phi in cfg.nodes[node].versionedPhiNode.keys():
                stacks[phi].pop()


    def phiDestruction(self, cfg):
        for nodeId in cfg.nodes:
            for phi in cfg.nodes[nodeId].versionedPhiNode:
                for parent in cfg.nodes[nodeId].versionedPhiNode[phi][1][0].keys():
                    cfg.nodes[parent].destructedPhi[phi] = (cfg.nodes[nodeId].versionedPhiNode[phi][0][0], cfg.nodes[nodeId].versionedPhiNode[phi][1][0][parent])




    # def explore(self, cfg, nodeId, visited, res):
    #     if not visited[nodeId]:
    #         visited[nodeId] = True
    #         res['str'] = res['str'] + str(nodeId) + "[ label=\"" + str(cfg.nodes[nodeId].stringSsa) + "\"] ;\n\t"
    #         for child in cfg.nodes[nodeId].next:
    #             if not visited[child]:
    #                 res['str'] = res['str'] + str(nodeId) + "  ->  " + str(child) + " ;\n\t"
    #                 self.explore(cfg, child, visited, res)
    #
    #
    # def generateFinalDotGraph(self, cfg):
    #     res = {"str": "digraph G {\n\n\t"}
    #     visited = dict()
    #     for nodeId in cfg.nodes:
    #         visited[nodeId] = False
    #     for nodeId in cfg.nodes:
    #         if not visited[nodeId]:
    #             self.explore(cfg, nodeId, visited, res)
    #     res['str'] = res['str'] + "\n}"
    #     self.stringSsa = res['str']
    #     return self.stringSsa




    def generateVersionedDotFile(self, cfg):
        res = "digraph G {\n\n\t"
        flagLastNode = -1
        for nodeId in cfg.nodes:
            flagLastNode = nodeId
            res = res + "\n\t" + str(nodeId) + "[ label=\"" + str(cfg.nodes[nodeId].stringSsa) + "\" "
            if self.helper.getRuleName(cfg.nodes[nodeId].ctx)=="condition":
                res = res + ", color=orange, shape=diamond"
            res = res + " ] ;\n\t\n\t"

            for child in cfg.nodes[nodeId].next:
                res = res + str(nodeId) + " -> " + str(child) + " ;\n\t"
        res = res + "0[ label=\"START\", shape=Msquare, color=green ]" + " ;\n\t"
        res = res + str(flagLastNode) + " -> EXIT ;"
        res = res + "EXIT[ shape=Msquare, color=red ]" + " ;\n\t"
        res = res + "\n}"
        return res

    def generateVersionedPhiNodeWalaDotFile(self, cfg):
        res = "digraph G {\n\n\t"
        flagLastNode = -1
        for nodeId in cfg.nodes:
            flagLastNode = nodeId
            res = res + "\n\t" + str(nodeId) + "[ label=\"" + str(cfg.nodes[nodeId].stringSsa)
            isTherePhiNode = False
            if len(cfg.nodes[nodeId].versionedPhiNode) > 0:
                isTherePhiNode = True
                tempDict = cfg.nodes[nodeId].versionedPhiNode
                tempStr = ""
                for key1 in tempDict.keys():
                    tempStr = "\\n" + str(tempDict[key1][0][0]) + " = Phi("
                    for key2 in tempDict[key1][1][0].keys():
                        tempStr = tempStr + ", " + tempDict[key1][1][0][key2]
                    tempStr = tempStr + ")"
                res = res + "\\nPhiNode(s)" + tempStr
            res = res + "\" "
            if isTherePhiNode:
                res = res + ", color=green"
            if self.helper.getRuleName(cfg.nodes[nodeId].ctx)=="condition":
                res = res + ", color=orange, shape=diamond"
            res = res + " ] ;\n\t\n\t"

            for child in cfg.nodes[nodeId].next:
                res = res + str(nodeId) + " -> " + str(child) + " ;\n\t"
        res = res + "\n\t0[ label=\"START\", shape=Msquare, color=green ]" + " ;\n\t"
        res = res + str(flagLastNode) + " -> EXIT ;"
        res = res + "EXIT[ shape=Msquare, color=red ]" + " ;\n\t"
        res = res + "\n}"
        return res

    def generateDestructedPhiNodeWalaDotFile(self, cfg):
        res = "digraph G {\n\n\t"
        flagLastNode = -1
        for nodeId in cfg.nodes:
            flagLastNode = nodeId
            res = res + "\n\t" + str(nodeId) + "[ label=\"" + str(cfg.nodes[nodeId].stringSsa)
            isThereDestructedPhi = False
            if len(cfg.nodes[nodeId].destructedPhi) > 0:
                isThereDestructedPhi = True
                tempDict = cfg.nodes[nodeId].destructedPhi
                tempStr = ""
                for key1 in tempDict.keys():
                    tempStr = "\\n" + str(tempDict[key1][0]) + " = " + str(tempDict[key1][1])
                res = res + "\\nDestructed PhiNode(s)" + tempStr
            res = res + "\" "
            if isThereDestructedPhi:
                res = res + ", color=green"
            if self.helper.getRuleName(cfg.nodes[nodeId].ctx)=="condition":
                res = res + ", color=orange, shape=diamond"
            res = res + " ] ;\n\t\n\t"

            for child in cfg.nodes[nodeId].next:
                res = res + str(nodeId) + " -> " + str(child) + " ;\n\t"
        res = res + "\n\t0[ label=\"START\", shape=Msquare, color=green ]" + " ;\n\t"
        res = res + str(flagLastNode) + " -> EXIT ;"
        res = res + "EXIT[ shape=Msquare, color=red ]" + " ;\n\t"
        res = res + "\n}"
        return res

    def _dfs(self, vertex, cfg):
        global time
        cfg.nodes[vertex].color = 'red'
        cfg.nodes[vertex].visited = time
        time +=1
        for v in cfg.nodes[vertex].next:
            if cfg.nodes[v].color == 'black':
                self._dfs(cfg.nodes[v].id, cfg)
        cfg.nodes[vertex].color = 'blue'
        cfg.nodes[vertex].visited = time
        time += 1
        

    def dfs(self, start, cfg):
        global time
        time = 1
        self._dfs(start, cfg)



    def dfs_path(self, start, goal, cfg, path = None):
        if path is None:
            path = [start]

        if start == goal:
            yield path

        for v in cfg.nodes[start].next:
            #path = path + [cfg.nodes[v].id]
            yield from self.dfs_path(v, goal, cfg, path + [v])
            #
            #nxt = v
            #sdfs_path(v, goal, cfg)

        #for next in cfg.nodes[start].id - set(path):
            #yield from dfs_path(cfg, next, goal, path + [next])           

    def SymblocVC(self, path, cfg):
        vcs = ' '
        for node in path:
            #mhrulename = self.getRuleName(
            #print(list(cfg.nodes[node].versionedRHS.values()))
            print(str(cfg.nodes[node].stringSsa))
            #print('*****\n')
        
                
            
