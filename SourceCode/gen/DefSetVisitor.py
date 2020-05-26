import sys
from inspect import signature
from antlr4 import *
from CLexer import CLexer
from CListener import CListener
from CParser import CParser
from CVisitor import CVisitor
from MyCFG import MyCFG
from MyRawCfgToGraph import MyRawCfgToGraph
from MyNode import MyNode
from RawCfgToCdg import RawCfgToCdg

from Chelper import MyHelper
from Cutility import MyUtility
from collections import defaultdict

class DefSetVisitor(CVisitor):
    def __init__(self, cfg):
        self.nodeCounter = 1
        self.textdict={}
        self.crude_cfg = ""
        self.cfg = cfg
        self.line_type_dict={}
        self.defVarSet = defaultdict(list)
        self.useVarSet = {}
        self.creatingdef = 0

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
                # print(self.nodeCounter, "\n", ctx.children[1].children[0].children[1].children[0].children[2].getText())  # function params     <------node
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
                # print(self.nodeCounter, "\n", ctx.children[0].children[0].children[1].children[0].children[2].getText())  # function params     <------node
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
            if ctx.children[2].getChildCount()==2:
                self.nodeCounter+=1
            elif ctx.children[2].getChildCount()==3:
                for i in range(3):
                    if str(ctx.children[2].children[i])!=';':
                        if i==0:
                            self.nodeCounter+=1
                        #self.crude_cfg = self.crude_cfg + "[ "
                        self.visit(ctx.children[2].children[i])
                        break

            elif ctx.children[2].getChildCount()==4:
                for i in range(4):
                    if str(ctx.children[2].children[i]) != ';':
                        #self.crude_cfg = self.crude_cfg + "[ "
                        self.visit(ctx.children[2].children[i])

            elif ctx.children[2].getChildCount() == 5:



                self.visit(ctx.children[2].children[4])

                self.crude_cfg = self.crude_cfg.rstrip()
                self.crude_cfg = self.crude_cfg + " "
                self.visit(ctx.children[2].children[2])
                self.crude_cfg = self.crude_cfg.rstrip()
                self.crude_cfg = self.crude_cfg + " "
                self.visit(ctx.children[2].children[0])
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
            #print("ctx.children[0] - ",str(ctx.children[0]))
            #print("str(ctx) - ",str(ctx))
            self.crude_cfg = self.crude_cfg + "[ if_"
            self.line_type_dict[self.nodeCounter] = "if"
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
        if ctx.getText() not in self.defVarSet[self.nodeCounter-1]:
            if ctx.getText()[-1] == ']':
                s = ctx.getText()
                for element in range(0, len(s)):
                    if s[element] == '[':
                        break
                s = s[:element] + "_arr"
                # print("updated variable name - ", s)
                if s not in self.defVarSet[self.nodeCounter]:
                    self.defVarSet[self.nodeCounter - 1].append(s)
            else:
            #print("adding to defset - ",ctx.getText())
                self.defVarSet[self.nodeCounter-1].append(ctx.getText())



    def visitForDeclaration(self, ctx):
        if ctx.getChildCount() > 1:
            # print(self.nodeCounter, "\n", ctx.getText())                        # <------node
            self.textdict[self.nodeCounter] = ctx.getText()
            self.crude_cfg = self.crude_cfg + str(self.nodeCounter) + " "
            self.cfg.nodes[self.nodeCounter] = MyNode(self.nodeCounter, ctx)
            #self.line_type_dict[self.nodeCounter] = "for_declaration"
            self.nodeCounter = self.nodeCounter + 1


    def visitExpression(self, ctx):
        #if ctx.getChildCount() > 1:
        # print(self.nodeCounter, "\n", ctx.getText())                        # <------node
        self.textdict[self.nodeCounter] = ctx.getText()
        self.crude_cfg = self.crude_cfg + str(self.nodeCounter) + " "
        self.cfg.nodes[self.nodeCounter] = MyNode(self.nodeCounter, ctx)
        self.line_type_dict[self.nodeCounter] = "expression"
        if ctx.getChildCount()==1:
            self.visit(ctx.children[0])
        else:
            self.visit(ctx.children[2])
            self.visit(ctx.children[0])
        if ctx.getChildCount() == 1:
            self.nodeCounter = self.nodeCounter + 1

    def visitAssignmentExpression(self, ctx):
        if ctx.getChildCount() > 1:
            # print(self.nodeCounter, "\n", ctx.getText())                        # <------node
            self.textdict[self.nodeCounter] = ctx.getText()
            self.crude_cfg = self.crude_cfg + str(self.nodeCounter) + " "
            self.cfg.nodes[self.nodeCounter] = MyNode(self.nodeCounter, ctx)
            self.line_type_dict[self.nodeCounter] = "assignment"
            #############
            # print("entering----------------------------")
            if ctx.children[0].getText() not in self.defVarSet[self.nodeCounter]:
                #print("assignment - ", ctx.children[0].getText()[-1])
                if ctx.children[0].getText()[-1] == ']' :
                    s = ctx.children[0].getText()
                    for element in range(0,len(s)):
                        if s[element] == '[':
                            break
                    s = s[:element] + "_arr"

                    if s not in self.defVarSet[self.nodeCounter]:
                        self.defVarSet[self.nodeCounter].append(s)

                else:
                    #print("what? - ", ctx.children[0].getText())
                    self.defVarSet[self.nodeCounter].append(ctx.children[0].getText())

            #############
            # self.nodeCounter = self.nodeCounter + 1
            #print("visitassignctx - ", ctx.children[2].)
            #self.visit(ctx.children[2])
        else:
            # print("(((((((((&&&&&&&&&&%ashish%%%%%%%%%%)))))))))",ctx.getChildCount())
            self.visit(ctx.children[0])


    def visitUnaryExpression(self, ctx):
        if ctx.getChildCount() > 1:
            if ctx.children[0].getText() == '++' or ctx.children[0].getText() == '--':
                if ctx.children[1].getText() not in self.defVarSet[self.nodeCounter]:
                    self.defVarSet[self.nodeCounter].append(ctx.children[1].getText())
        else:
            self.visit(ctx.children[0])

    def visitPostfixExpression(self, ctx):
        #n = ctx.getChildCount()
        #print("****<postfix>******")
        #print("nodecounter - ", self.nodeCounter)
        #print("defVarSet[self.nodecounter] - ", self.defVarSet[self.nodeCounter])
        #print("child count - ",n)
        #for i in range(n):
            #print("ctx.children[",i,"].getText() = ", ctx.children[i].getText())
        #print("***</postfix>****")
        if ctx.getChildCount() > 1:
            if ctx.children[1].getText() == '++' or ctx.children[1].getText() == '--':
                if ctx.children[0].getText() not in self.defVarSet[self.nodeCounter]:
                    if ctx.children[0].getText()[-1] == ']':
                        s = ctx.children[0].getText()
                        for element in range(0, len(s)):
                            if s[element] == '[':
                                break
                        s = s[:element] + "_arr"
                        #print("updated variable name - ", s)
                        if s not in self.defVarSet[self.nodeCounter]:
                            self.defVarSet[self.nodeCounter].append(s)

                        #if ctx.getChildCount() == 4 and ctx.children[2].getText() not in self.useVarSet[self.nodeCounter]:
                           # self.useVarSet[self.nodeCounter].append(ctx.children[2].getText())

                    else:
                        #print("what? - ", ctx.children[0].getText())
                        self.defVarSet[self.nodeCounter].append(ctx.children[0].getText())

        #if ctx.getChildCount() == 4:
            #if ctx.children[1].getText() == '[' and ctx.children[3].getText() == ']':
                #print("Inside added array logic....")
                #if ctx.children[0].getText() not in self.defVarSet[self.nodeCounter]:
                    #print("append should be successful...")
                    #self.defVarSet[self.nodeCounter].append(ctx.children[0].getText()+"_arr")


    def visitForExpression(self, ctx):
        #if ctx.getChildCount() > 1:
        # print(self.nodeCounter, "\n", ctx.getText())                        # <------node
        self.textdict[self.nodeCounter] = ctx.getText()
        #self.crude_cfg = self.crude_cfg + str(self.nodeCounter) + " "
        self.cfg.nodes[self.nodeCounter] = MyNode(self.nodeCounter, ctx)
        if ctx.getChildCount() > 1:
            self.visit(ctx.children[0])
            self.visit(ctx.children[2])
        else:
            self.visit(ctx.children[0])
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