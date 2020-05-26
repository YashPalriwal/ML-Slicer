
import queue

from CVisitor import CVisitor

from Chelper import MyHelper

time = 0

class MyUtility():


    def __init__(self, helper):
        self.helper = helper
        self.defset={}
        self.useset={}



    def generateDefSet(self, cfg):
        #res = {}
        for nodeId in cfg.nodes:
            self.defset[nodeId] = []
            #print(nodeId)
            #cfg.nodes[nodeId].variableSet = set(self.helper.getVariableSet(cfg.nodes[nodeId].ctx))#, nodeId) )
            #res = res.union(cfg.nodes[nodeId].variableSet)
            #cfg.nodes[nodeId].variableRHS = self.helper.generateRHS(cfg.nodes[nodeId].ctx)#, nodeId)
            #print(cfg.nodes[nodeId].variableRHS)
            cfg.nodes[nodeId].variableLHS = self.helper.generateLHS(cfg.nodes[nodeId].ctx)#, nodeId)
            for i in cfg.nodes[nodeId].variableLHS:
                self.defset[nodeId].append(i)
            #res = res.union(cfg.nodes[nodeId].variableLHS)

        return self.defset


    def generateUseSet(self, cfg):
        #res = set()
        for nodeId in cfg.nodes:
            self.useset[nodeId] = []
            #print(nodeId)
            #cfg.nodes[nodeId].variableSet = set(self.helper.getVariableSet(cfg.nodes[nodeId].ctx))#, nodeId) )
            #res = res.union(cfg.nodes[nodeId].variableSet)
            cfg.nodes[nodeId].variableRHS = self.helper.generateRHS(cfg.nodes[nodeId].ctx)#, nodeId)
            #print(cfg.nodes[nodeId].variableRHS)
            #cfg.nodes[nodeId].variableLHS = self.helper.generateLHS(cfg.nodes[nodeId].ctx)#, nodeId)
            for i in cfg.nodes[nodeId].variableRHS:
                self.useset[nodeId].append(i)

            #res = res.union(cfg.nodes[nodeId].variableRHS)

        return self.useset





    def generateVariableSet(self, cfg):
        res = set()
        for nodeId in cfg.nodes:
            #print(nodeId)
            cfg.nodes[nodeId].variableSet = set(self.helper.getVariableSet(cfg.nodes[nodeId].ctx))#, nodeId) )   #TODO: remove nodeId
            res = res.union(cfg.nodes[nodeId].variableSet)
            cfg.nodes[nodeId].variableRHS = self.helper.generateRHS(cfg.nodes[nodeId].ctx)#, nodeId)   #TODO: remove nodeId
            #print(cfg.nodes[nodeId].variableRHS)
            cfg.nodes[nodeId].variableLHS = self.helper.generateLHS(cfg.nodes[nodeId].ctx)#, nodeId)   #TODO: remove nodeId

        return res





    def getVariableDict(self, cfg):
        res = set()
        for nodeId in cfg.nodes:
            res = res.union(cfg.nodes[nodeId].variableSet)
        resDict = dict()

        for var in res:
            resDict[var] = 0
        return resDict





                
            
