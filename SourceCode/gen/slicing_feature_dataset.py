import sys
import random
import itertools
from inspect import signature
from antlr4 import *
from CLexer import CLexer
from CListener import CListener
from CParser import CParser
from CVisitor import CVisitor
import os
from MyCFG import MyCFG
from MyRawCfgToGraph import MyRawCfgToGraph
from MyNode import MyNode
from RawCfgToCdg import RawCfgToCdg

from DefSetVisitor import DefSetVisitor
from UseSetVisitor import UseSetVisitor


#import numpy as np
#import pandas as pd
# import sklearn.gaussian_process as gp
# from scipy.stats import norm
# from scipy.optimize import minimize
#
# from sklearn.metrics import accuracy_score
# from sklearn.ensemble import RandomForestClassifier,AdaBoostClassifier
# from sklearn.tree import DecisionTreeClassifier
# from sklearn.gaussian_process import GaussianProcessClassifier
# from sklearn.neighbors import KNeighborsClassifier
# from sklearn.gaussian_process.kernels import RBF
# from sklearn.gaussian_process.kernels import Matern
# from sklearn.svm import SVC
# from sklearn.naive_bayes import GaussianNB
# from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
# from xgboost import XGBClassifier
# from sklearn.linear_model import LogisticRegression
#from sklearn_extensions.extreme_learning_machines.elm import GenELMClassifier
#from sklearn_extensions.extreme_learning_machines.random_layer import RBFRandomLayer


class Defdeclaration(CVisitor):

    def __init__(self):
        self.x=''

    def getdefvar(self):
        return self.x

    def visitDirectDeclarator(self, ctx):
        self.x = ctx.getText()
        # print("ash",self.x)


class Declaration(CVisitor):

    def visitInitDeclarator(self, ctx:CParser.InitDeclaratorContext):
        if ctx.getChildCount()==3:
            #print(ctx.children[0].getText())
            return ctx.children[0].getText()



class MyCVisitor(CVisitor):
    def __init__(self):
        self.VarList=[]


    #def addlist(self, new_value):
            #self.VarList.append(new_value)

    def getVarList(self):
        return self.VarList

    #def visitDeclaration(self, ctx):
        #if (ctx.getChildCount()==3):
            #print("test1")
            #print(ctx.children[1].children[1])
            #if(ctx.children[1].children[1].getText()==","):
                #self.VarList.append(ctx.children[1].children[2].children[0].getText())
                #self.VarList.append(ctx.children[1].children[0].children[0].children[0].getText())
    def visitDirectDeclarator(self, ctx):
        if(ctx.getChildCount()==1):
            self.VarList.append(ctx.getText())


class MyCVisitor2(CVisitor):
    def __init__(self, cfg):
        self.nodeCounter = 1
        self.textdict={}
        self.crude_cfg = ""
        self.cfg = cfg
        self.line_type_dict={}
        self.defVarSet = {0:[],1:[],2:[],3:[],4:[],5:[],6:[],7:[],8:[]}
        self.useVarSet = {}
        self.creatingdef = 0
        self.noElse = 15

    def getCrudeCfg(self):
        return self.crude_cfg

    def getStatementType(self):
        return self.line_type_dict


    def getdict(self):
        return self.textdict

    def visitTranslationUnit(self, ctx):    # functions
        if(ctx.getChildCount() > 1):
            #print("***")
            self.crude_cfg = self.crude_cfg + "[ " #+ str(ctx.children[1].children[0].children[1].children[0].children[0].getText())
            #print(ctx.children[1].children[0].children[1].children[0].children[0].getText())    # function name
            if(ctx.children[1].children[0].children[1].children[0].getChildCount() > 3):
                #print(self.nodeCounter, "\n", ctx.children[1].children[0].children[1].children[0].children[2].getText())  # function params     <------node
                self.crude_cfg = self.crude_cfg  + str(self.nodeCounter)
                self.cfg.nodes[self.nodeCounter] = MyNode(self.nodeCounter,ctx)
                self.nodeCounter = self.nodeCounter + 1
            else:
                self.crude_cfg = self.crude_cfg + " 0"
                self.cfg.nodes[0] = MyNode(0)
            #print("***", ctx.children[1].children[0].children[1].getText())
            #print("***")
            self.crude_cfg = self.crude_cfg + " [ "
            self.visit(ctx.children[1])
            self.crude_cfg = self.crude_cfg + " ]"
            self.crude_cfg = self.crude_cfg + " ]\n"
        else:
            #print("***")
            self.crude_cfg = self.crude_cfg + "[ " #+ str(ctx.children[0].children[0].children[1].children[0].children[0].getText())
            # print(ctx.children[0].children[0].children[1].children[0].children[0].getText())  # function name
            if (ctx.children[0].children[0].children[1].children[0].getChildCount() > 3):
                #print(self.nodeCounter, "\n", ctx.children[0].children[0].children[1].children[0].children[2].getText())  # function params     <------node
                self.crude_cfg = self.crude_cfg  + str(self.nodeCounter)
                self.cfg.nodes[self.nodeCounter] = MyNode(self.nodeCounter, ctx)
                self.nodeCounter = self.nodeCounter + 1
            else:
                self.crude_cfg = self.crude_cfg + " 0"
                self.cfg.nodes[0] = MyNode(0)
            #print("***", ctx.children[0].children[0].children[1].getText())
            #print("***")
        self.crude_cfg = self.crude_cfg + " [ "
        self.visit(ctx.children[0])
        self.crude_cfg = self.crude_cfg + " ]"
        self.crude_cfg = self.crude_cfg + " ]\n"

    def visitIterationStatement(self, ctx):     # dowhile, for, while
        if (str(ctx.children[0]) == "while"):
            #print("----while_cond")
            self.crude_cfg = self.crude_cfg + "[ while_"
            self.line_type_dict[self.nodeCounter] = "while"
            self.visit(ctx.children[2])

            #print("--while_true")
            self.crude_cfg = self.crude_cfg + "[ "
            self.visit(ctx.children[4])
            self.crude_cfg = self.crude_cfg + " ] "
            self.crude_cfg = self.crude_cfg + " ] "
        elif(str(ctx.children[0]) == "for"):
            #print("----for_cond")
            self.crude_cfg = self.crude_cfg + "[ for_"
            self.line_type_dict[self.nodeCounter] = "for"
            self.visit(ctx.children[2].children[0])

            self.crude_cfg = self.crude_cfg.rstrip()
            self.crude_cfg = self.crude_cfg + " "
            self.visit(ctx.children[2].children[2])
            self.crude_cfg = self.crude_cfg.rstrip()
            self.crude_cfg = self.crude_cfg + " "
            self.visit(ctx.children[2].children[4])
            #print("--for_true")
            self.crude_cfg = self.crude_cfg + "[ "
            self.visit(ctx.children[4])
            self.crude_cfg = self.crude_cfg + " ] "
            self.crude_cfg = self.crude_cfg + " ] "
        elif(str(ctx.children[0]) == "do"):
            #print("----dowhile_cond")
            self.crude_cfg = self.crude_cfg + "[ while_"
            self.line_type_dict[self.nodeCounter] = "dowhile"
            self.visit(ctx.children[4])

            #print("--dowhile_true")
            self.crude_cfg = self.crude_cfg + "[ "
            self.visit(ctx.children[1])
            self.crude_cfg = self.crude_cfg + " ] "
            self.crude_cfg = self.crude_cfg + " ] "

    def visitSelectionStatement(self, ctx):     # switch, if
        if (str(ctx.children[0]) == "if"):
            #print("----if_cond")
            self.crude_cfg = self.crude_cfg + "[ if_"
            self.line_type_dict[self.nodeCounter] = "if"
            ############# no else part ##############
            self.noElse = self.nodeCounter
            # print("AAAAAAAAAAAANNNNNNNNNNNNNNNNDDDDDDDDDDDDDD",self.noElse)
            ############# no else part ##############
            self.visit(ctx.children[2])
            #print("---if_true")
            self.crude_cfg = self.crude_cfg + "[ "
            self.visit(ctx.children[4])
            self.crude_cfg = self.crude_cfg + " ] "
            self.crude_cfg = self.crude_cfg + "[ "
            if (ctx.getChildCount()>5 and str(ctx.children[5]) == "else"):
                # print("---if_false")
                self.visit(ctx.children[6])
            ############# no else part ##############
            else:
                node = MyNode(self.noElse,None)
                self.cfg.addNode(node)
                self.crude_cfg = self.crude_cfg + str(self.noElse)
                self.noElse = self.noElse-1
            ############# no else part ##############
            self.crude_cfg = self.crude_cfg + " ] "
            self.crude_cfg = self.crude_cfg + " ] "
        if (str(ctx.children[0]) == "switch"):
            #print("----switch_cond")
            self.visit(ctx.children[2])
            #print("---switch_cases:")
            self.visit(ctx.children[4])

    def visitDeclaration(self, ctx):
        if ctx.getChildCount() > 1:
            # print(self.nodeCounter, "\n", ctx.getText())                        # <------node
            self.textdict[self.nodeCounter] = ctx.getText()
            self.crude_cfg = self.crude_cfg + str(self.nodeCounter) + " "
            self.cfg.nodes[self.nodeCounter] = MyNode(self.nodeCounter, ctx)
            self.line_type_dict[self.nodeCounter]="declaration"
            self.nodeCounter = self.nodeCounter+1
            ########
            self.visit(ctx.children[1])

    ##########visit function#######
    def visitDirectDeclarator(self,ctx):
        self.defVarSet[self.nodeCounter-1].append(ctx.getText())

    def visitForDeclaration(self, ctx):
        if ctx.getChildCount() > 1:
            # print(self.nodeCounter, "\n", ctx.getText())                        # <------node
            self.textdict[self.nodeCounter] = ctx.getText()
            self.crude_cfg = self.crude_cfg + str(self.nodeCounter) + " "
            self.cfg.nodes[self.nodeCounter] = MyNode(self.nodeCounter, ctx)
            #self.line_type_dict[self.nodeCounter] = "for_declaration"
            self.nodeCounter = self.nodeCounter + 1

    def visitAssignmentExpression(self, ctx):
        if ctx.getChildCount() > 1:
            # print(self.nodeCounter, "\n", ctx.getText())                        # <------node
            self.textdict[self.nodeCounter] = ctx.getText()
            self.crude_cfg = self.crude_cfg + str(self.nodeCounter) + " "
            self.cfg.nodes[self.nodeCounter] = MyNode(self.nodeCounter, ctx)
            self.line_type_dict[self.nodeCounter] = "assignment"
            self.nodeCounter = self.nodeCounter + 1

    def visitExpression(self, ctx):
        #if ctx.getChildCount() > 1:
        # print(self.nodeCounter, "\n", ctx.getText())                        # <------node
        self.textdict[self.nodeCounter] = ctx.getText()
        self.crude_cfg = self.crude_cfg + str(self.nodeCounter) + " "
        self.cfg.nodes[self.nodeCounter] = MyNode(self.nodeCounter, ctx)
        self.line_type_dict[self.nodeCounter] = "expression"
        self.nodeCounter = self.nodeCounter + 1


    def visitForExpression(self, ctx):
        #if ctx.getChildCount() > 1:
        # print(self.nodeCounter, "\n", ctx.getText())                        # <------node
        self.textdict[self.nodeCounter] = ctx.getText()
        #self.crude_cfg = self.crude_cfg + str(self.nodeCounter) + " "
        self.cfg.nodes[self.nodeCounter] = MyNode(self.nodeCounter, ctx)
        #self.nodeCounter = self.nodeCounter + 1

    def visitJumpStatement(self, ctx):
        if ctx.getChildCount() > 1:
            # print(self.nodeCounter, "\n", ctx.getText())                        # <------node
            self.textdict[self.nodeCounter] = ctx.getText()
            self.crude_cfg = self.crude_cfg + str(self.nodeCounter) + " "
            self.cfg.nodes[self.nodeCounter] = MyNode(self.nodeCounter, ctx)
            self.line_type_dict[self.nodeCounter] = "return_statement"
            self.nodeCounter = self.nodeCounter + 1

    def visitLabeledStatement(self, ctx):
        if str(ctx.children[0]) == "case":
            # print("--case : ", ctx.children[1].getText())
            # print(self.nodeCounter, "\n", ctx.children[1].getText())                        # <------node
            self.nodeCounter = self.nodeCounter + 1
            self.visit(ctx.children[3])
        if str(ctx.children[0]) == "default":
            # print("--default : ")
            self.visit(ctx.children[2])


class MyCVisitor3(CVisitor):
    def __init__(self,parser, cfg, utility ):
        self.parser = parser
        self.utility = utility
        self.nodeCounter = 1
        self.textdict = {}
        self.crude_cfg = ""
        self.cfg = cfg
        self.varDict = dict()
        self.cfg.addNode(MyNode(self.nodeCounter, None))


    def getCrudeCfg(self):
        return self.crude_cfg

    def getdict(self):
        return self.textdict

    def visitTranslationUnit(self, ctx):  # functions
        node = MyNode(self.nodeCounter, ctx)
        if (ctx.getChildCount() > 1):
            # print("***")
            self.crude_cfg = self.crude_cfg + "[ "  # + str(ctx.children[1].children[0].children[1].children[0].children[0].getText())
            # print(ctx.children[1].children[0].children[1].children[0].children[0].getText())    # function name
            if (ctx.children[1].children[0].children[1].children[0].getChildCount() > 3):
                #print(self.nodeCounter, "\n", ctx.children[1].children[0].children[1].children[0].children[2].getText())  # function params     <------node
                self.crude_cfg = self.crude_cfg + str(self.nodeCounter)
                self.cfg.nodes[self.nodeCounter] = MyNode(self.nodeCounter, ctx)
                self.nodeCounter = self.nodeCounter + 1
            else:
                self.crude_cfg = self.crude_cfg + " 0"
                self.cfg.nodes[0] = MyNode(0)
            # print("***", ctx.children[1].children[0].children[1].getText())
            # print("***")
            self.crude_cfg = self.crude_cfg + " [ "
            self.visit(ctx.children[1])
            self.crude_cfg = self.crude_cfg + " ]"
            self.crude_cfg = self.crude_cfg + " ]\n"
        else:
            # print("***")
            self.crude_cfg = self.crude_cfg + "[ "  # + str(ctx.children[0].children[0].children[1].children[0].children[0].getText())
            # print(ctx.children[0].children[0].children[1].children[0].children[0].getText())  # function name
            if (ctx.children[0].children[0].children[1].children[0].getChildCount() > 3):
                # print(self.nodeCounter, "\n", ctx.children[0].children[0].children[1].children[0].children[2].getText())  # function params     <------node
                self.crude_cfg = self.crude_cfg + str(self.nodeCounter)
                self.cfg.nodes[self.nodeCounter] = MyNode(self.nodeCounter, ctx)
                self.nodeCounter = self.nodeCounter + 1
            else:
                self.crude_cfg = self.crude_cfg + " 0"
                self.cfg.nodes[0] = MyNode(0)
            # print("***", ctx.children[0].children[0].children[1].getText())
            # print("***")
        self.crude_cfg = self.crude_cfg + " [ "
        self.visit(ctx.children[0])
        self.crude_cfg = self.crude_cfg + " ]"
        self.crude_cfg = self.crude_cfg + " ]\n"

    def visitIterationStatement(self, ctx):  # dowhile, for, while
        if (str(ctx.children[0]) == "while"):
            # print("----while_cond")
            self.crude_cfg = self.crude_cfg + "[ while_"
            self.visit(ctx.children[2])
            # print("--while_true")
            self.crude_cfg = self.crude_cfg + "[ "
            self.visit(ctx.children[4])
            self.crude_cfg = self.crude_cfg + " ] "
            self.crude_cfg = self.crude_cfg + " ] "
        elif (str(ctx.children[0]) == "for"):
            # print("----for_cond")
            self.crude_cfg = self.crude_cfg + "[ for_"
            self.visit(ctx.children[2].children[0])
            self.crude_cfg = self.crude_cfg.rstrip()
            self.crude_cfg = self.crude_cfg + " "
            self.visit(ctx.children[2].children[2])
            self.crude_cfg = self.crude_cfg.rstrip()
            self.crude_cfg = self.crude_cfg + " "
            self.visit(ctx.children[2].children[4])
            # print("--for_true")
            self.crude_cfg = self.crude_cfg + "[ "
            self.visit(ctx.children[4])
            self.crude_cfg = self.crude_cfg + " ] "
            self.crude_cfg = self.crude_cfg + " ] "
        elif (str(ctx.children[0]) == "do"):
            # print("----dowhile_cond")
            self.crude_cfg = self.crude_cfg + "[ while_"
            self.visit(ctx.children[4])
            # print("--dowhile_true")
            self.crude_cfg = self.crude_cfg + "[ "
            self.visit(ctx.children[1])
            self.crude_cfg = self.crude_cfg + " ] "
            self.crude_cfg = self.crude_cfg + " ] "

    def visitSelectionStatement(self, ctx):  # switch, if
        if (str(ctx.children[0]) == "if"):
            # print("----if_cond")
            self.crude_cfg = self.crude_cfg + "[ if_"
            self.visit(ctx.children[2])
            # print("---if_true")
            self.crude_cfg = self.crude_cfg + "[ "
            self.visit(ctx.children[4])
            self.crude_cfg = self.crude_cfg + " ] "
            self.crude_cfg = self.crude_cfg + "[ "
            if (ctx.getChildCount() > 5 and str(ctx.children[5]) == "else"):
                # print("---if_false")
                self.visit(ctx.children[6])
            self.crude_cfg = self.crude_cfg + " ] "
            self.crude_cfg = self.crude_cfg + " ] "
        if (str(ctx.children[0]) == "switch"):
            # print("----switch_cond")
            self.visit(ctx.children[2])
            # print("---switch_cases:")
            self.visit(ctx.children[4])

    def visitDeclaration(self, ctx):
        node = MyNode(self.nodeCounter, ctx)
        if ctx.getChildCount() > 1:
            # print(self.nodeCounter, "\n", ctx.getText())  # <------node
            self.textdict[self.nodeCounter] = ctx.getText()
            self.crude_cfg = self.crude_cfg + str(self.nodeCounter) + " "
            self.cfg.nodes[self.nodeCounter] = MyNode(self.nodeCounter, ctx)
            self.nodeCounter = self.nodeCounter + 1

    def visitForDeclaration(self, ctx):
        node = MyNode(self.nodeCounter, ctx)
        if ctx.getChildCount() > 1:
            # print(self.nodeCounter, "\n", ctx.getText())  # <------node
            self.textdict[self.nodeCounter] = ctx.getText()
            self.crude_cfg = self.crude_cfg + str(self.nodeCounter) + " "
            self.cfg.nodes[self.nodeCounter] = MyNode(self.nodeCounter, ctx)
            self.nodeCounter = self.nodeCounter + 1

    def visitAssignmentExpression(self, ctx):
        node = MyNode(self.nodeCounter, ctx)

        if ctx.getChildCount() > 1:
            # print(self.nodeCounter, "\n", ctx.getText())  # <------node
            self.textdict[self.nodeCounter] = ctx.getText()
            self.crude_cfg = self.crude_cfg + str(self.nodeCounter) + " "
            self.cfg.nodes[self.nodeCounter] = MyNode(self.nodeCounter, ctx)
            self.nodeCounter = self.nodeCounter + 1

    def visitExpression(self, ctx):
        node = MyNode(self.nodeCounter, ctx)
        # if ctx.getChildCount() > 1:
        # print(self.nodeCounter, "\n", ctx.getText())  # <------node
        self.textdict[self.nodeCounter] = ctx.getText()
        self.crude_cfg = self.crude_cfg + str(self.nodeCounter) + " "
        self.cfg.nodes[self.nodeCounter] = MyNode(self.nodeCounter, ctx)
        self.nodeCounter = self.nodeCounter + 1

    def visitForExpression(self, ctx):
        # if ctx.getChildCount() > 1:
        # print(self.nodeCounter, "\n", ctx.getText())  # <------node
        self.textdict[self.nodeCounter] = ctx.getText()
        # self.crude_cfg = self.crude_cfg + str(self.nodeCounter) + " "
        self.cfg.nodes[self.nodeCounter] = MyNode(self.nodeCounter, ctx)
        # self.nodeCounter = self.nodeCounter + 1

    def visitJumpStatement(self, ctx):
        node = MyNode(self.nodeCounter, ctx)
        if ctx.getChildCount() > 1:
            # print(self.nodeCounter, "\n", ctx.getText())  # <------node
            self.textdict[self.nodeCounter] = ctx.getText()
            self.crude_cfg = self.crude_cfg + str(self.nodeCounter) + " "
            self.cfg.nodes[self.nodeCounter] = MyNode(self.nodeCounter, ctx)
            self.nodeCounter = self.nodeCounter + 1

    def visitLabeledStatement(self, ctx):
        node = MyNode(self.nodeCounter, ctx)
        if str(ctx.children[0]) == "case":
            # print("--case : ", ctx.children[1].getText())
            # print(self.nodeCounter, "\n", ctx.children[1].getText())  # <------node
            self.nodeCounter = self.nodeCounter + 1
            self.visit(ctx.children[3])
        if str(ctx.children[0]) == "default":
            # print("--default : ")
            self.visit(ctx.children[2])



class MyCVisitor4(CVisitor):
    def __init__(self):
        self.nodeCounter = 1
        self.textdict={}
        self.crude_cfg = ""

    def getdict(self):
        return self.textdict

    def getCrudeCfg(self):

        return self.crude_cfg

    def visitTranslationUnit(self, ctx):    # functions
        if(ctx.getChildCount() > 1):
            #print("***")
            self.crude_cfg = self.crude_cfg + "[ " + str(ctx.children[1].children[0].children[1].children[0].children[0].getText())
            #print(ctx.children[1].children[0].children[1].children[0].children[0].getText())    # function name
            if(ctx.children[1].children[0].children[1].children[0].getChildCount() > 3):
                #print(self.nodeCounter, "\n", ctx.children[1].children[0].children[1].children[0].children[2].getText())  # function params     <------node
                self.crude_cfg = self.crude_cfg + "_" + str(self.nodeCounter)
                self.nodeCounter = self.nodeCounter + 1
            else:
                self.crude_cfg = self.crude_cfg + " 0"
            #print("***", ctx.children[1].children[0].children[1].getText())
            #print("***")
            self.crude_cfg = self.crude_cfg + " [ "
            self.visit(ctx.children[1])
            self.crude_cfg = self.crude_cfg + " ]"
            self.crude_cfg = self.crude_cfg + " ]\n"
        else:
            #print("***")
            self.crude_cfg = self.crude_cfg + "[ " + str(ctx.children[0].children[0].children[1].children[0].children[0].getText())
            #print(ctx.children[0].children[0].children[1].children[0].children[0].getText())  # function name
            if (ctx.children[0].children[0].children[1].children[0].getChildCount() > 3):
                #print(self.nodeCounter, "\n", ctx.children[0].children[0].children[1].children[0].children[2].getText())  # function params     <------node
                self.crude_cfg = self.crude_cfg + "_" + str(self.nodeCounter)
                self.nodeCounter = self.nodeCounter + 1
            else:
                self.crude_cfg = self.crude_cfg + " 0"
            #print("***", ctx.children[0].children[0].children[1].getText())
            #print("***")
        self.crude_cfg = self.crude_cfg + " [ "
        self.visit(ctx.children[0])
        self.crude_cfg = self.crude_cfg + " ]"
        self.crude_cfg = self.crude_cfg + " ]\n"

    def visitIterationStatement(self, ctx):     # dowhile, for, while
        if (str(ctx.children[0]) == "while"):
            #print("----while_cond")
            self.crude_cfg = self.crude_cfg + "[ while "
            self.visit(ctx.children[2])
            #print("--while_true")
            self.crude_cfg = self.crude_cfg + "[ "
            self.visit(ctx.children[4])
            self.crude_cfg = self.crude_cfg + " ] "
            self.crude_cfg = self.crude_cfg + " ] "
        elif(str(ctx.children[0]) == "for"):
            #print("----for_cond")
            self.crude_cfg = self.crude_cfg + "[ for "
            self.visit(ctx.children[2].children[0])
            self.crude_cfg = self.crude_cfg.rstrip()
            self.crude_cfg = self.crude_cfg + " "
            self.visit(ctx.children[2].children[2])
            self.crude_cfg = self.crude_cfg.rstrip()
            self.crude_cfg = self.crude_cfg + " "
            self.visit(ctx.children[2].children[4])
            #print("--for_true")
            self.crude_cfg = self.crude_cfg + "[ "
            self.visit(ctx.children[4])
            self.crude_cfg = self.crude_cfg + " ] "
            self.crude_cfg = self.crude_cfg + " ] "
        elif(str(ctx.children[0]) == "do"):
            #print("----dowhile_cond")
            self.crude_cfg = self.crude_cfg + "[ while  "
            self.visit(ctx.children[4])
            #print("--dowhile_true")
            self.crude_cfg = self.crude_cfg + "[ "
            self.visit(ctx.children[1])
            self.crude_cfg = self.crude_cfg + " ] "
            self.crude_cfg = self.crude_cfg + " ] "

    def visitSelectionStatement(self, ctx):     # switch, if
        if (str(ctx.children[0]) == "if"):
            #print("----if_cond")
            self.crude_cfg = self.crude_cfg + "[ if "
            self.visit(ctx.children[2])
            #print("---if_true")
            self.crude_cfg = self.crude_cfg + "[ "
            self.visit(ctx.children[4])
            self.crude_cfg = self.crude_cfg + " ] "
            self.crude_cfg = self.crude_cfg + "[ "
            if (ctx.getChildCount()>5 and str(ctx.children[5]) == "else"):
                #print("---if_false")
                self.visit(ctx.children[6])
            self.crude_cfg = self.crude_cfg + " ] "
            self.crude_cfg = self.crude_cfg + " ] "
        if (str(ctx.children[0]) == "switch"):
            #print("----switch_cond")
            self.visit(ctx.children[2])
            #print("---switch_cases:")
            self.visit(ctx.children[4])

    def visitDeclaration(self, ctx):
        if ctx.getChildCount() > 1:
            #print(self.nodeCounter, "\n", ctx.getText())                        # <------node
            self.textdict[self.nodeCounter]= ctx.getText()
            self.crude_cfg = self.crude_cfg + str(self.nodeCounter) + " "
            self.nodeCounter = self.nodeCounter+1

    def visitForDeclaration(self, ctx):
        if ctx.getChildCount() > 1:
            #print(self.nodeCounter, "\n", ctx.getText())                        # <------node
            self.textdict[self.nodeCounter] = ctx.getText()
            self.crude_cfg = self.crude_cfg + str(self.nodeCounter) + " "
            self.nodeCounter = self.nodeCounter + 1

    def visitAssignmentExpression(self, ctx):
        if ctx.getChildCount() > 1:
            #print(self.nodeCounter, "\n", ctx.getText())                        # <------node
            self.textdict[self.nodeCounter] = ctx.getText()
            self.crude_cfg = self.crude_cfg + str(self.nodeCounter) + " "
            self.nodeCounter = self.nodeCounter + 1

    def visitExpression(self, ctx):
        #if ctx.getChildCount() > 1:
        #print(self.nodeCounter, "\n", ctx.getText())                        # <------node
        self.textdict[self.nodeCounter] = ctx.getText()
        self.crude_cfg = self.crude_cfg + str(self.nodeCounter) + " "
        self.nodeCounter = self.nodeCounter + 1

    #def visitForExpression(self, ctx):
        #if ctx.getChildCount() > 1:
        #print(self.nodeCounter, "\n", ctx.getText())                        # <------node
        #self.crude_cfg = self.crude_cfg + str(self.nodeCounter) + " "
        #self.nodeCounter = self.nodeCounter + 1

    def visitJumpStatement(self, ctx):
        if ctx.getChildCount() > 1:
            #print(self.nodeCounter, "\n", ctx.getText())                        # <------node
            self.textdict[self.nodeCounter] = ctx.getText()
            self.crude_cfg = self.crude_cfg + str(self.nodeCounter) + " "
            self.nodeCounter = self.nodeCounter + 1

    def visitLabeledStatement(self, ctx):
        if str(ctx.children[0]) == "case":
            #print("--case : ", ctx.children[1].getText())
            #print(self.nodeCounter, "\n", ctx.children[1].getText())                        # <------node
            self.nodeCounter = self.nodeCounter + 1
            self.visit(ctx.children[3])
        if str(ctx.children[0]) == "default":
            #print("--default : ")
            self.visit(ctx.children[2])



















def findall(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]


def feature_calculation(variable,linenumber,cfg_textdict,cfg_list,total_lines,variables_list,potential_lines,defset,useset):
    vari = variable
    linenum = linenumber
    index_linenum = cfg_list.index(linenum)
    # print(index_linenum)


    # act_str = actual_slice_dictionary[str((vari, linenum)).replace(' ', '')]
    # print(vari, linenum)
    # print(act_str)

    #################################    var_dependency_list and findsubstr function         #######################################################################################3

    var_dependencylist = []

    # print(type(vari))
    # print(potential_line_features)

    def findsubstr(p, s):
        '''Yields all the positions of
        the pattern p in the string s.'''
        i = s.find(p)
        while i != -1:
            yield i
            i = s.find(p, i + 1)

    temp_indices = []
    var_dependencylist.append(vari)
    for i in range(len(potential_lines) - 1, -1, -1):
        strline = cfg_textdict[potential_lines[i]]
        temporary_ind = [j for j in findsubstr(vari + '=', strline)]
        temporary_ind2 = [j for j in findsubstr(vari + '+=', strline)]
        temporary_ind3 = [j for j in findsubstr(vari + '\=', strline)]
        temporary_ind4 = [j for j in findsubstr(vari + '-=', strline)]
        temporary_ind5 = [j for j in findsubstr(vari + '*=', strline)]
        temporary_ind6 = [j for j in findsubstr(vari + '%=', strline)]
        if (len(temporary_ind) > 0 or len(temporary_ind2) > 0 or len(temporary_ind3) > 0 or len(
                temporary_ind4) > 0 or len(temporary_ind5) > 0 or len(temporary_ind6) > 0):
            for temp_str in variables_list:
                indices = [k for k in findsubstr(temp_str, strline)]
                wrong_indices = [g for g in findsubstr(',' + temp_str, strline)]
                if len(indices) > 0:
                    if len(wrong_indices) == 0:
                        if (temp_str not in var_dependencylist):
                            var_dependencylist.append(temp_str)

    #print(var_dependencylist)

    ###################################   FEATURES #############################################

    line_features1 = [[0] * 29 for i in range(0, total_lines)]

    ##########################       FEATURE-1: WHETHER LINE CONTAINS AN "IF"  STATEMENT AND FEATURE-2: IF YES THEN ARE VARIABLES FROM var_dependencylist INVOLVED ? ########
    for i in range(1, total_lines + 1):
        temp_index = cfg_list.index(str(i))
        strline = cfg_textdict[i]
        # print(temp_index)
        if (cfg_list[temp_index - 1] == "if"):
            # print("yes")
            line_features1[i - 1][0] = 1
            for temp_str in var_dependencylist:
                if temp_str in defset[i] or temp_str in useset[i]:
                    line_features1[i - 1][1] = 1

                ######## changed #################
                #temporary_ind = [j for j in findsubstr(temp_str, strline)]
                #if len(temporary_ind) > 0:
                    #line_features1[i - 1][1] = 1
                ###################################
    ###########################  FEATURE-3 : WHETHER LINE CONTAINS A "WHILE" STATEMENT AND FEATURE-4: IF YES THEN ARE VARIABLES FROM var_dependencylist INVOLVED ? #########################
    for i in range(1, total_lines + 1):
        temp_index = cfg_list.index(str(i))
        strline = cfg_textdict[i]
        # print(temp_index)
        if (cfg_list[temp_index - 1] == "while"):
            # print("yes")
            line_features1[i - 1][2] = 1
            for temp_str in var_dependencylist:
                if temp_str in defset[i] or temp_str in useset[i]:
                    line_features1[i - 1][3] = 1

                ########### changed ##################
                #temporary_ind = [j for j in findsubstr(temp_str, strline)]
                #if len(temporary_ind) > 0:
                    #line_features1[i - 1][3] = 1
                #######################################
    ######################### FEATURE-5 : WHETHER LINE CONTAINS A "FOR"  STATEMENT AND FEATURE-6: IF YES THEN ARE VARIABLES FROM var_dependencylist INVOLVED ? ############################
    for i in range(1, total_lines + 1):
        temp_index = cfg_list.index(str(i))
        strline = cfg_textdict[i]
        # print(temp_index)
        if (cfg_list[temp_index - 1] == "for"):
            # print("yes")
            line_features1[i - 1][4] = 1
            for temp_str in var_dependencylist:
                if temp_str in defset[i] or temp_str in useset[i]:
                    line_features1[i - 1][5] = 1


                # temporary_ind = [j for j in findsubstr(temp_str, strline)]
                # # print(temporary_ind)
                # # print(strline)
                # if len(temporary_ind) > 0:
                #     line_features1[i - 1][5] = 1

    ######################### FEATURE-7 : WHETHER LINE CONTAINS A "SCANF"  STATEMENT AND FEATURE-8: IF YES THEN ARE VARIABLES FROM var_dependencylist INVOLVED ? ############################
    for i in range(1, total_lines + 1):
        temp_index = cfg_list.index(str(i))
        strline = cfg_textdict[i]
        #print(type(strline))
        #print("---------ashish---------",len(strline))
        # print(temp_index)
        if 'scanf' in strline:

            line_features1[i - 1][6] = 1
            indices = findall(strline, '&')
            for j in indices:
                for var in var_dependencylist:
                    if var in strline[j + 1:]:
                        line_features1[i - 1][7] = 1





    ########################  CONTROL FEATURES: WHETHER LINE IS UNDER CONTRL OF ANOTHER IF,WHILE,FOR STATEMENT ? ##########

    ################### PREREQUISITE : INDICES OF WHILE, IF, FOR  #########################

    if_indices = []
    while_indices = []
    for_indices = []
    main_indices = []
    switch_indices = []
    for i in range(len(cfg_list)):
        if (cfg_list[i] == "if"):
            if_indices.append(i)
        if (cfg_list[i] == "while"):
            while_indices.append(i)
        if (cfg_list[i] == "for"):
            for_indices.append(i)
        if (cfg_list[i] == "main"):
            main_indices.append(i)
        if (cfg_list[i] == "switch"):
            switch_indices.append(i)

    ########################  FEATURE-9: WHETHER LINE IS UNDER CONTRL OF ANOTHER IF STATEMENT ? ##########
    if len(if_indices) > 0:
        for i in range(len(if_indices)):
            j = if_indices[i] + 2
            countopen = 1
            while (countopen > 0):
                if (cfg_list[j] == '['):
                    countopen = countopen + 1
                if (cfg_list[j] == ']'):
                    countopen = countopen - 1

                if (cfg_list[j].isdigit()):
                    line_features1[int(cfg_list[j]) - 1][8] = 1
                j = j + 1

    ########################  FEATURE-10: WHETHER LINE IS UNDER CONTRL OF ANOTHER WHILE STATEMENT ? ##########
    if len(while_indices) > 0:
        for i in range(len(while_indices)):
            j = while_indices[i] + 2
            countopen = 1
            while (countopen > 0):
                if (cfg_list[j] == '['):
                    countopen = countopen + 1
                if (cfg_list[j] == ']'):
                    countopen = countopen - 1

                if (cfg_list[j].isdigit()):
                    line_features1[int(cfg_list[j]) - 1][9] = 1
                j = j + 1

    ########################  FEATURE-11: WHETHER LINE IS UNDER CONTRL OF ANOTHER FOR STATEMENT ? ##########

    if len(for_indices) > 0:
        for i in range(len(for_indices)):
            j = for_indices[i] + 2
            countopen = 1
            while (countopen > 0):
                if (cfg_list[j] == '['):
                    countopen = countopen + 1
                if (cfg_list[j] == ']'):
                    countopen = countopen - 1

                if (cfg_list[j].isdigit()):
                    line_features1[int(cfg_list[j]) - 1][10] = 1
                j = j + 1

    # ##################   FEATURE-12: WHETHER LINE IS UNDER CONTRL OF ANOTHER SWITCH STATEMENT ?   ##############
    #
    # if len(switch_indices) > 0:
    #     for i in range(len(switch_indices)):
    #         j = switch_indices[i] + 2
    #         countopen = 1
    #         while (countopen > 0):
    #             if (cfg_list[j] == '['):
    #                 countopen = countopen + 1
    #             if (cfg_list[j] == ']'):
    #                 countopen = countopen - 1
    #
    #             if (cfg_list[j].isdigit()):
    #                 line_features1[int(cfg_list[j]) - 1][11] = 1
    #             j = j + 1

    ############################################################################################################

    ###### FEATURE-12: WHETHER LINE CONTAINS BREAK STATEMENT? & FEATURE-13: WHETHER LINE CONTAINS CONTINUE STATEMENT? & FEATURE-14: WHETHER LINE CONTAINS UNARY(++) STATEMENT ?  FEATURE-15: WHETHER LINE CONTAINS UNARY(--) ##############

    for i in range(1, total_lines + 1):
        temp_index = cfg_list.index(str(i))
        strline = cfg_textdict[i]
        temporary_ind = [j for j in findsubstr("break;", strline)]
        temporary_ind1 = [j for j in findsubstr("continue;", strline)]
        if (len(temporary_ind) > 0):
            line_features1[i - 1][11] = 1;
        if (len(temporary_ind1) > 0):
            line_features1[i - 1][12] = 1;
        for temp_str in var_dependencylist:
            temporary_ind2 = [j for j in findsubstr(temp_str + "++", strline)]
            temporary_ind3 = [j for j in findsubstr(temp_str + "--", strline)]
            temporary_ind4 = [j for j in findsubstr("++" + temp_str, strline)]
            temporary_ind5 = [j for j in findsubstr("--" + temp_str, strline)]
        if len(temporary_ind2) > 0  or len(temporary_ind4) > 0 :
            line_features1[i - 1][13] = 1;

        if len(temporary_ind3) > 0  or len(temporary_ind5) > 0 :
            line_features1[i - 1][14] = 1;

    # print(line_features2)

    ##################   FEATURE-16: Does the line define the variables from var_dependency_list ?  AND FEATURE-17:  Does the line only use the variables from var_dependency_list ###
    for i in range(1, total_lines + 1):
        strline = cfg_textdict[i]
        # print(strline)
        for temp_str in var_dependencylist:
            if temp_str in defset[i]:
                line_features1[i - 1][15] = 1



            temporary_ind2 = [j for j in findsubstr(temp_str + '=', strline)]
            temporary_ind3 = [j for j in findsubstr(temp_str + '+=', strline)]
            temporary_ind4 = [j for j in findsubstr(temp_str + '/=', strline)]
            temporary_ind5 = [j for j in findsubstr(temp_str + '-=', strline)]
            temporary_ind6 = [j for j in findsubstr(temp_str + '*=', strline)]
            temporary_ind7 = [j for j in findsubstr(temp_str + '%=', strline)]
            temporary_ind8 = [j for j in findsubstr(temp_str + "==", strline)]

            # if len(set(temporary_ind2) - set(temporary_ind8)) > 0 or len(temporary_ind3) > 0 or len(
            #         temporary_ind4) > 0 or len(temporary_ind5) > 0 or len(temporary_ind6) > 0 or len(
            #         temporary_ind7) > 0:
            #     line_features1[i - 1][15] = 1

            temporary_ind9 = [j for j in findsubstr(">=", strline)]
            temporary_ind10 = [j for j in findsubstr("<=", strline)]
            temporary_ind11 = [j for j in findsubstr(">", strline)]
            temporary_ind12 = [j for j in findsubstr("<", strline)]
            temporary_ind13 = [j for j in findsubstr("!=", strline)]
            temporary_ind14 = [j for j in findsubstr('=', strline)]
            temporary_ind15 = [j for j in findsubstr("==", strline)]
            temporary_ind16 = [j for j in findsubstr(temp_str, strline)]

            for temp_str in var_dependencylist:
                if temp_str in defset[i]:
                    line_features1[i - 1][16] = 1

            # if len(temporary_ind9) > 0 or len(temporary_ind10) > 0 or len(temporary_ind11) > 0 or len(
            #         temporary_ind12) > 0 or len(temporary_ind13) > 0 or len(temporary_ind15) > 0:
            #     if len(temporary_ind16) > 0:
            #         line_features1[i - 1][16] = 1
            else:
                if len(temporary_ind14) > 0 and len(temporary_ind16) > 0:
                    for j in temporary_ind16:
                        if any(j > x for x in temporary_ind14):
                            line_features1[i - 1][16] = 1
                            break

    ###### FEATURE-18,19,20,21,22,23 : COMBINATION OF FEATURE-16 AND FEATURE-17 WITH Feature-9,10,11,12(defined and being controlled by if/while/for/switch ##############
    for i in range(1, total_lines + 1):
        if line_features1[i - 1][15] == 1:
            if line_features1[i - 1][8] == 1:
                line_features1[i - 1][17] = 1
            if line_features1[i - 1][9] == 1:
                line_features1[i - 1][18] = 1
            if line_features1[i - 1][10] == 1:
                line_features1[i - 1][19] = 1
            # if line_features1[i - 1][11] == 1:
            #     line_features1[i - 1][20] = 1
        if line_features1[i - 1][16] == 1:
            if line_features1[i - 1][8] == 1:
                line_features1[i - 1][20] = 1
            if line_features1[i - 1][9] == 1:
                line_features1[i - 1][21] = 1
            if line_features1[i - 1][10] == 1:
                line_features1[i - 1][22] = 1
            # if line_features1[i - 1][11] == 1:
            #     line_features1[i - 1][24] = 1

    ###########  FEATURE-24 IS THE LINE CONTAINING POINTER VARIABLE DECLARATION ###############

    data_type_list = ['char', 'int', 'short', 'long', 'float', 'double', 'signed', 'unsigned']
    pointer_var_list = []
    for i in range(1, total_lines + 1):
        strline = cfg_textdict[i]
        for temp_var in variables_list:
            for dtype in data_type_list:
                # print(dtype+'*'+temp_var)
                temporary_ind = [j for j in findsubstr(dtype + '*' + temp_var, strline)]
                temporary_ind2 = [j for j in findsubstr(',' + '*' + temp_var, strline)]
                if len(temporary_ind) > 0 or len(temporary_ind2) > 0:
                    line_features1[i - 1][23] = 1
                    if temp_var not in pointer_var_list:
                        pointer_var_list.append(temp_var)
    # print(pointer_var_list)
    # print(line_features1)

    ####  FEATURE-25 IS THE LINE INVOLVES DEFINITION OF VARIABLES FROM var_dependencylist using pointer variables ###############
    for i in range(1, total_lines + 1):
        strline = cfg_textdict[i]
        for temp_var in variables_list:
            for p_var in pointer_var_list:
                temporary_ind = [j for j in findsubstr(temp_var + '=', strline)]
                temporary_ind2 = [j for j in findsubstr(p_var, strline)]
                for j in temporary_ind:
                    for k in range(j + 2, len(strline)):
                        if k in temporary_ind2:
                            line_features1[i - 1][24] = 1
                            break

    #######   FEATURE-26,27,28,29: COMBINATION OF IF/WHILE/FOR/SWITCH FEATURES AND WHETHER THEY ARE UNDER THE CONTROL OF SOME IF/WHILE/FOR/SWITCH RESPECTIVELY #################
    for i in range(1, total_lines + 1):
        if line_features1[i - 1][1] and line_features1[i - 1][8]:
            line_features1[i - 1][25] = 1
        if line_features1[i - 1][3] and line_features1[i - 1][9]:
            line_features1[i - 1][26] = 1
        if line_features1[i - 1][5] and line_features1[i - 1][10]:
            line_features1[i - 1][27] = 1
        if line_features1[i - 1][7] and line_features1[i - 1][11]:
            line_features1[i - 1][28] = 1



    ####################### POTENTIAL LINE FEATURES ###################
    #print(potential_lines)
    potential_line_features = []
    for i in range(total_lines):
        if i + 1 in potential_lines:
            potential_line_features.append(line_features1[i])
    #print(vari, linenum)
    #print("himanshu", line_features1)
    #print( potential_line_features)

    return potential_line_features




def main():

    problem_list=[]





    #####################  INITIALIZATION #####################################################################
    inclusion_factor_overall = 0.0
    redundancy_factor_overall=0.0
    optimal_factors_overall = (inclusion_factor_overall,redundancy_factor_overall)

    w = []
    for i in range(0, 29):
        w.append(random.uniform(-1, 1))
    #print(w)
    wmax = w
    wmin = w
    count_progs=0
    svcdata=open("slicing_data_current.txt", "w")
    for filename in os.listdir("new_c_prog"):
        count_progs+=1


        c_fileName = "new_c_prog/"+filename
        input_file = FileStream(c_fileName)
        lexer = CLexer(input_file)
        stream = CommonTokenStream(lexer)
        parser = CParser(stream)
        tree = parser.compilationUnit()
        #print(tree.toStringTree(recog=parser))


        #print("Start Walking...")
        v = MyCVisitor()
        v.visit(tree)
        #print(v.getVarList())

        v1 = MyCVisitor4()
        v1.visit(tree)
        #print("\n\n\n", v1.getCrudeCfg())
        #vari = input("Enter a variable name: ")
        #linenum = input("Enter a line number: ")

        cfg1 = MyCFG()

        defObj = DefSetVisitor(cfg1)
        defObj.visit(tree)
        useSetObj = UseSetVisitor(cfg1)
        useSetObj.visit(tree)
        defset = defObj.defVarSet
        # print(defset)
        useset = useSetObj.useVarSet









        ###############   TOTAL LINES ##################################
        cfg_string = v1.getCrudeCfg()
        cfg_textdict = v1.getdict()
        #print(cfg_textdict)
        #print(cfg_string)
        cfg_list = cfg_string.split(' ')
        #print(cfg_list)
        cfg_list = [x for x in cfg_list if x != '']
        #print(cfg_list)
        total_lines = 0
        for i in range(len(cfg_list) - 1, -1, -1):
            if cfg_list[i].isdigit():
                total_lines = int(cfg_list[i])
                break
        #print(total_lines)

        #############################################################3
        #line_features = [[0] * 8 for i in range(0,total_lines)]
        # print(line_features)


























     ######################################################################################



    ##################  ALL PREREQUISITE CALCULATIONS #####################################
        variables_list = v.getVarList()
        c_outfile = "testing_slice_module/" + filename[:-2] + ".txt"
        actual_slice_file = open(c_outfile, "r")
        # print(actual_slice_file)

        #
        actual_slice_text = actual_slice_file.read().splitlines()
        # print(actual_slice_text)
        actual_slice_dictionary = {}
        count1=0
        for i in actual_slice_text:
            count1+=1
            #print(count1)
            key_value = i.split(":")
            #print("ashish ranjasn",key_value)
            #print(i)
            #print(key_value[0])
            #print(key_value[1])

            # key_value[1].replace(",\n",'')
            #print(type(actual_slice_dictionary))
            actual_slice_dictionary[key_value[0]] = key_value[1]
        #print("akranjanam",actual_slice_dictionary)
        #new_slice = [i.replace('"', '') for i in actual_slice_dictionary]
        #print("Ashish",actual_slice_dictionary)

        for key, value in actual_slice_dictionary.items():
            #print(len(actual_slice_dictionary))
            temp_str1 = ''
            temp_str2=''
            for i in range(2,len(key)):
                if key[i]=="'":
                    break
                else:
                    temp_str1=temp_str1+(key[i])
            for j in range(i+3,len(key)):
                if key[j]=="'":
                    break
                else:
                    temp_str2+=key[j]
            #print("ashishnew",temp_str1,temp_str2)
            vari = temp_str1
            linenum=temp_str2
            #print(vari)
            #print(linenum)



            ################################### potential_lines ###########################
            #print(linenum," ",cfg_list)
            index_linenum = cfg_list.index(linenum)
            potential_lines = list(range(1, int(linenum)))
            potential_flag = 0
            for i in range(index_linenum, -1, -1):
                if cfg_list[i] == ']':
                    break
                if cfg_list[i] == '[':
                    # print("yes")

                    if cfg_list[i - 2] == "while":
                        j = i - 2
                        countopen = 1
                        # print("yes")
                        while (countopen > 0):
                            if (cfg_list[j] == '['):
                                countopen = countopen + 1
                            if (cfg_list[j] == ']'):
                                countopen = countopen - 1
                            # print("yes")
                            if (cfg_list[j].isdigit()):
                                # print("hello")
                                if (cfg_list[j] != linenum and int(cfg_list[j]) not in potential_lines):
                                    potential_lines.append(int(cfg_list[j]))
                            j = j + 1
                        break
            #print(potential_lines)
            act_str = actual_slice_dictionary[str((vari, linenum)).replace(' ', '')]
            #print(vari, linenum)
            #print(act_str)

            ########################### RANDOM SAMPLING ALGORITHM FOR CODE-BASE #######################################





            potential_line_scores = [0] * len(potential_lines)
            #print(potential_line_scores)
            potential_line_features = feature_calculation(vari,linenum,cfg_textdict,cfg_list,total_lines,variables_list,potential_lines,defset,useset)
            #print(potential_lines)
            #print(potential_line_features)


            #print(potential_lines)
            #print("shikhar",optimal_abstraction_lines)
            actual_slice = eval(act_str)
            #print(actual_slice)
            #print(type(actual_slice))
            #print(type(actual_slice))
            # print(abstraction_scores)
            #print(optimal_abstraction_indices)
            actual_output = []
            #print("shikhar",vari)

            size_of_slice = len(actual_slice)


            for i in range(len(potential_lines)):
                #svcdata.write("prog_" + str(count_progs) + "\t")
                svcdata.write(vari + "\t" + linenum + "\t")

                svcdata.write(str(potential_lines[i])+"\t")
                for j in potential_line_features[i]:
                    svcdata.write(str(j)+"\t")
                if str(potential_lines[i]) in act_str:
                    svcdata.write("1"+"\n")
                else:
                    svcdata.write("0"+"\n")


    svcdata.close()
    #df=pd.read_csv("slicing_data_current.txt",delimiter='\t')
    #print(df)
    #df.to_csv("random_csv")

    # data=pd.read_csv("slicing_svc_data_half.txt", header=None, delimiter="\t")
    # xtrain = data.iloc[0:1672, 3:32]
    # ytrain = data.iloc[0:1671, 32]
    # xtest = data.iloc[1672:, 3:32]
    # ytest = data.iloc[1672:, 32]
    #
    #
    # #################################################### SUPPORT VECTOR CLASSIFIER #################################
    #
    # clf_svc = SVC(gamma='auto')
    # clf_svc.fit(xtrain, ytrain)
    # pred1 = clf_svc.predict(xtest)
    # svc_accuracy = accuracy_score(ytest, pred1)
    # print("SVC ACCURACY IS : ",svc_accuracy)
    #
    #
    # ################################################### RANDOM FOREST CLASSIFIER ###################################
    #
    # clf_rfc = RandomForestClassifier(n_estimators=100, max_depth=2, random_state=0)
    # clf_rfc.fit(xtrain, ytrain)
    # pred2 = clf_rfc.predict(xtest)
    # rfc_accuracy = accuracy_score(ytest, pred2)
    # print("RANDOM FOREST ACCURACY IS: ",rfc_accuracy)
    #
    #
    # #################################################### DECISION TREE CLASSIFIER ######################################
    # clf_dtc =  DecisionTreeClassifier(max_depth=5)
    # clf_dtc.fit(xtrain,ytrain)
    # pred3 = clf_dtc.predict(xtest)
    # dtc_accuracy = accuracy_score(ytest,pred3)
    # print("DECISION TREE ACCURACY IS: ",dtc_accuracy)
    #
    #
    # ################################################## GAUSSIAN PROCESS RBF CLASSIFIER #################################
    #
    # # clf_gpc =  GaussianProcessClassifier(1.0 * RBF(1.0))
    # # clf_gpc.fit(xtrain,ytrain)
    # # pred4 = clf_gpc.predict(xtest)
    # # gpc_accuracy = accuracy_score(ytest,pred4)
    # # print("GAUSSIAN PROCESS ACCURACY IS: ",gpc_accuracy)
    #
    # ################################################ GAUSSIAN NAIVE BAYES CLASSIFIER ###################################
    #
    # clf_gnb = GaussianNB()
    # clf_gnb.fit(xtrain,ytrain)
    # pred5 = clf_gnb.predict(xtest)
    # gnb_accuracy = accuracy_score(ytest,pred5)
    # print("GAUSSIAN NAIVE BAYES ACCURACY IS: ",gnb_accuracy)
    #
    # ################################################# ADABOOST CLASSIFIER ##############################################
    # clf_abc = AdaBoostClassifier()
    # clf_abc.fit(xtrain,ytrain)
    # pred6 = clf_abc.predict(xtest)
    # abc_accuracy = accuracy_score(ytest,pred6)
    # print("ADABOOST ACCURACY IS: ",abc_accuracy)
    #
    #
    # #################################################### XGBOOST CLASSIFIER   ##########################################
    #
    # xgbc = XGBClassifier()
    # xgbc.fit(xtrain, ytrain)
    # pred7 = xgbc.predict(xtest)
    # xgb_accuracy= accuracy_score(ytest, pred7)
    # print("XGBOOST ACCURACY IS: ",xgb_accuracy)
    #
    # #################################################  QUADRATIC DISCRIMINANT ANALYSIS CLASSIFIER  #####################
    #
    # qdac = QuadraticDiscriminantAnalysis()
    # qdac.fit(xtrain,ytrain)
    # pred8 = qdac.predict(xtest)
    # qda_accuracy = accuracy_score(ytest,pred8)
    # print("QUADRATIC DISCRIMINANT ANALYSIS ACCURACY IS ",qda_accuracy)
    #
    # ##############################################  LOGISTIC REGRESSION AS CLASSIFIER ##################################
    # clf_lrc = LogisticRegression(random_state=0, solver='lbfgs',multi_class = 'multinomial')
    # clf_lrc.fit(xtrain,ytrain)
    # pred9 = clf_lrc.predict(xtest)
    # lrc_accuracy = accuracy_score(ytest,pred9)
    # print("LOGISTIC REGRESSION ACCURACY IS: ",lrc_accuracy)
    #
    # ########################################## K- NEAREST NEIGHBOURS CLASSIFICATION ####################################
    #
    # clf_knnc =  KNeighborsClassifier(3)
    # clf_knnc.fit(xtrain,ytrain)
    # pred10 = clf_knnc.predict(xtest)
    # knnc_accuracy = accuracy_score(ytest,pred10)
    # print("K NEAREST NEIGHBOURS ACCURACY IS: ",knnc_accuracy)
    #
    #
    # ################################################### DEEP LEARNING MODELS ###########################################
    #
    # ############################# MULTI LAYER PERCEPTRON ###############################################################
    #





























































if __name__ == '__main__':
    main()
