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
import os
import random
from skopt.utils import use_named_args
from skopt import gp_minimize
# from skopt.space import
import time
from Chelper import MyHelper
from Cutility import MyUtility
from DefSetVisitor import DefSetVisitor
from UseSetVisitor import UseSetVisitor
from numpy import arange
from numpy import vstack
from numpy import argmax
from numpy import asarray
from numpy.random import normal
#from numpy.random import random
from scipy.stats import norm
from sklearn.gaussian_process import GaussianProcessRegressor
from warnings import catch_warnings
from warnings import simplefilter
from matplotlib import pyplot



class Defdeclaration(CVisitor):

    def __init__(self):
        self.x = ''

    def getdefvar(self):
        return self.x

    def visitDirectDeclarator(self, ctx):
        self.x = ctx.getText()
    # print("ash",self.x)


class Declaration(CVisitor):

    def visitInitDeclarator(self, ctx: CParser.InitDeclaratorContext):
        if ctx.getChildCount() == 3:
            # print(ctx.children[0].getText())
            return ctx.children[0].getText()


class MyCVisitor(CVisitor):
    def __init__(self):
        self.VarList = []

    # def addlist(self, new_value):
    # self.VarList.append(new_value)

    def getVarList(self):
        return self.VarList

    # def visitDeclaration(self, ctx):
    # if (ctx.getChildCount()==3):
    # print("test1")
    # print(ctx.children[1].children[1])
    # if(ctx.children[1].children[1].getText()==","):
    # self.VarList.append(ctx.children[1].children[2].children[0].getText())
    # self.VarList.append(ctx.children[1].children[0].children[0].children[0].getText())
    def visitDirectDeclarator(self, ctx):
        if (ctx.getChildCount() == 1):
            self.VarList.append(ctx.getText())
        # print("appending variable - ", ctx.getText())

        elif ctx.getChildCount() == 4:
            # print("array variable - ", ctx.children[0].children[0].getText())
            self.VarList.append(ctx.children[0].children[0].getText() + "_arr")


class MyCVisitor2(CVisitor):
    def __init__(self, cfg):
        self.nodeCounter = 1
        self.textdict = {}
        self.crude_cfg = ""
        self.cfg = cfg
        self.line_type_dict = {}
        self.defVarSet = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: []}
        self.useVarSet = {}
        self.creatingdef = 0
        self.noElse = 15

    def getCrudeCfg(self):
        # print("crude_cfg - ", self.crude_cfg)
        return self.crude_cfg

    def getStatementType(self):
        return self.line_type_dict

    def getdict(self):
        return self.textdict

    def visitTranslationUnit(self, ctx):  # functions
        if (ctx.getChildCount() > 1):
            # print("***")
            self.crude_cfg = self.crude_cfg + "[ "  # + str(ctx.children[1].children[0].children[1].children[0].children[0].getText())
            # print(ctx.children[1].children[0].children[1].children[0].children[0].getText())    # function name
            if (ctx.children[1].children[0].children[1].children[0].getChildCount() > 3):
                print(self.nodeCounter, "\n", ctx.children[1].children[0].children[1].children[0].children[
                    2].getText())  # function params     <------node
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
                print(self.nodeCounter, "\n", ctx.children[0].children[0].children[1].children[0].children[
                    2].getText())  # function params     <------node
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
            self.line_type_dict[self.nodeCounter] = "while"
            self.visit(ctx.children[2])

            # print("--while_true")
            self.crude_cfg = self.crude_cfg + "[ "
            self.visit(ctx.children[4])
            self.crude_cfg = self.crude_cfg + " ] "
            self.crude_cfg = self.crude_cfg + " ] "
        elif (str(ctx.children[0]) == "for"):
            # print("----for_cond")
            self.crude_cfg = self.crude_cfg + "[ for_"
            self.line_type_dict[self.nodeCounter] = "for"
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
            self.line_type_dict[self.nodeCounter] = "dowhile"
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
            self.line_type_dict[self.nodeCounter] = "if"
            ############# no else part ##############
            self.noElse = self.nodeCounter

            ############# no else part ##############
            self.visit(ctx.children[2])
            # print("---if_true")
            self.crude_cfg = self.crude_cfg + "[ "
            self.visit(ctx.children[4])
            self.crude_cfg = self.crude_cfg + " ] "
            self.crude_cfg = self.crude_cfg + "[ "
            if (ctx.getChildCount() > 5 and str(ctx.children[5]) == "else"):
                # print("---if_false")
                self.visit(ctx.children[6])
            ############# no else part ##############
            else:  # no need to create node for else block in case of simple if statements
                node = MyNode(self.noElse, None)
                self.cfg.addNode(node)
                self.crude_cfg = self.crude_cfg + str(self.noElse)
                self.noElse = self.noElse - 1
            ############# no else part ##############
            self.crude_cfg = self.crude_cfg + " ] "
            self.crude_cfg = self.crude_cfg + " ] "
        if (str(ctx.children[0]) == "switch"):  # switch statement not working properly
            # print("----switch_cond")
            self.visit(ctx.children[2])
            # print("---switch_cases:")
            self.visit(ctx.children[4])

    def visitDeclaration(self, ctx):
        if ctx.getChildCount() > 1:
            # print(self.nodeCounter, "\n", ctx.getText())                        # <------node
            self.textdict[self.nodeCounter] = ctx.getText()
            self.crude_cfg = self.crude_cfg + str(self.nodeCounter) + " "
            self.cfg.nodes[self.nodeCounter] = MyNode(self.nodeCounter, ctx)
            self.line_type_dict[self.nodeCounter] = "declaration"
            self.nodeCounter = self.nodeCounter + 1
            ########
            self.visit(ctx.children[1])

    ##########visit function#######
    def visitDirectDeclarator(self, ctx):
        self.defVarSet[self.nodeCounter - 1].append(ctx.getText())

    def visitForDeclaration(self, ctx):
        if ctx.getChildCount() > 1:
            # print(self.nodeCounter, "\n", ctx.getText())                        # <------node
            self.textdict[self.nodeCounter] = ctx.getText()
            self.crude_cfg = self.crude_cfg + str(self.nodeCounter) + " "
            self.cfg.nodes[self.nodeCounter] = MyNode(self.nodeCounter, ctx)
            # self.line_type_dict[self.nodeCounter] = "for_declaration"
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
        # if ctx.getChildCount() > 1:
        # print(self.nodeCounter, "\n", ctx.getText())                        # <------node
        self.textdict[self.nodeCounter] = ctx.getText()
        self.crude_cfg = self.crude_cfg + str(self.nodeCounter) + " "
        self.cfg.nodes[self.nodeCounter] = MyNode(self.nodeCounter, ctx)
        self.line_type_dict[self.nodeCounter] = "expression"
        self.nodeCounter = self.nodeCounter + 1

    def visitForExpression(self, ctx):
        # if ctx.getChildCount() > 1:
        # print(self.nodeCounter, "\n", ctx.getText())                        # <------node
        self.textdict[self.nodeCounter] = ctx.getText()
        # self.crude_cfg = self.crude_cfg + str(self.nodeCounter) + " "
        self.cfg.nodes[self.nodeCounter] = MyNode(self.nodeCounter, ctx)

    # self.nodeCounter = self.nodeCounter + 1

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


def findall(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]


def feature_calculation(variable, linenumber, cfg_textdict, cfg_list, total_lines, variables_list, potential_lines):
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

    # print(var_dependencylist)

    ###################################   FEATURES #############################################

    line_features1 = [[0] * 31 for i in range(0, total_lines)]

    ##########################       FEATURE-1: WHETHER LINE CONTAINS AN "IF"  STATEMENT AND FEATURE-2: IF YES THEN ARE VARIABLES FROM var_dependencylist INVOLVED ? ########
    for i in range(1, total_lines + 1):
        temp_index = cfg_list.index(str(i))
        strline = cfg_textdict[i]
        # print(temp_index)
        if (cfg_list[temp_index - 1] == "if"):
            # print("yes")
            line_features1[i - 1][0] = 1
            for temp_str in var_dependencylist:
                temporary_ind = [j for j in findsubstr(temp_str, strline)]
                if len(temporary_ind) > 0:
                    line_features1[i - 1][1] = 1

    ###########################  FEATURE-3 : WHETHER LINE CONTAINS A "WHILE" STATEMENT AND FEATURE-4: IF YES THEN ARE VARIABLES FROM var_dependencylist INVOLVED ? #########################
    for i in range(1, total_lines + 1):
        temp_index = cfg_list.index(str(i))
        strline = cfg_textdict[i]
        # print(temp_index)
        if (cfg_list[temp_index - 1] == "while"):
            # print("yes")
            line_features1[i - 1][2] = 1
            for temp_str in var_dependencylist:
                temporary_ind = [j for j in findsubstr(temp_str, strline)]
                if len(temporary_ind) > 0:
                    line_features1[i - 1][3] = 1

    ######################### FEATURE-5 : WHETHER LINE CONTAINS A "FOR"  STATEMENT AND FEATURE-6: IF YES THEN ARE VARIABLES FROM var_dependencylist INVOLVED ? ############################
    for i in range(1, total_lines + 1):
        temp_index = cfg_list.index(str(i))
        strline = cfg_textdict[i]
        # print(temp_index)
        if (cfg_list[temp_index - 1] == "for"):
            # print("yes")
            line_features1[i - 1][4] = 1
            for temp_str in var_dependencylist:
                temporary_ind = [j for j in findsubstr(temp_str, strline)]
                # print(temporary_ind)
                # print(strline)
                if len(temporary_ind) > 0:
                    line_features1[i - 1][5] = 1

    ######################### FEATURE-7 : WHETHER LINE CONTAINS A "SWITCH"  STATEMENT AND FEATURE-8: IF YES THEN ARE VARIABLES FROM var_dependencylist INVOLVED ? ############################
    for i in range(1, total_lines + 1):
        temp_index = cfg_list.index(str(i))
        strline = cfg_textdict[i]
        # print(temp_index)
        if (cfg_list[temp_index - 1] == "switch"):
            # print("yes")
            line_features1[i - 1][6] = 1
            for temp_str in var_dependencylist:
                temporary_ind = [j for j in findsubstr(temp_str, strline)]
                # print(temporary_ind)
                # print(strline)
                if len(temporary_ind) > 0:
                    line_features1[i - 1][7] = 1

    ########################  CONTROL FEATURES: WHETHER LINE IS UNDER CONTRL OF ANOTHER IF,WHILE,FOR,SWITCH STATEMENT ? ##########

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

    ##################   FEATURE-12: WHETHER LINE IS UNDER CONTRL OF ANOTHER SWITCH STATEMENT ?   ##############

    if len(switch_indices) > 0:
        for i in range(len(switch_indices)):
            j = switch_indices[i] + 2
            countopen = 1
            while (countopen > 0):
                if (cfg_list[j] == '['):
                    countopen = countopen + 1
                if (cfg_list[j] == ']'):
                    countopen = countopen - 1

                if (cfg_list[j].isdigit()):
                    line_features1[int(cfg_list[j]) - 1][11] = 1
                j = j + 1

    ############################################################################################################

    ###### FEATURE-13: WHETHER LINE CONTAINS BREAK STATEMENT? & FEATURE-14: WHETHER LINE CONTAINS CONTINUE STATEMENT? & FEATURE-15: WHETHER LINE CONTAINS UNARY STATEMENT ?  ##############

    for i in range(1, total_lines + 1):
        temp_index = cfg_list.index(str(i))
        strline = cfg_textdict[i]
        temporary_ind = [j for j in findsubstr("break;", strline)]
        temporary_ind1 = [j for j in findsubstr("continue;", strline)]
        if (len(temporary_ind) > 0):
            line_features1[i - 1][12] = 1;
        if (len(temporary_ind1) > 0):
            line_features1[i - 1][13] = 1;
        for temp_str in var_dependencylist:
            temporary_ind2 = [j for j in findsubstr(temp_str + "++", strline)]
            temporary_ind3 = [j for j in findsubstr(temp_str + "--", strline)]
            temporary_ind4 = [j for j in findsubstr("++" + temp_str, strline)]
            temporary_ind5 = [j for j in findsubstr("--" + temp_str, strline)]
        if len(temporary_ind2) > 0 or len(temporary_ind3) > 0 or len(temporary_ind4) > 0 or len(temporary_ind5) > 0:
            line_features1[i - 1][14] = 1;
    # print(line_features2)

    ##################   FEATURE-16: Does the line define the variables from var_dependency_list ?  AND FEATURE-17:  Does the line only use the variables from var_dependency_list ###
    for i in range(1, total_lines + 1):
        strline = cfg_textdict[i]
        # print(strline)
        for temp_str in var_dependencylist:
            temporary_ind2 = [j for j in findsubstr(temp_str + '=', strline)]
            temporary_ind3 = [j for j in findsubstr(temp_str + '+=', strline)]
            temporary_ind4 = [j for j in findsubstr(temp_str + '/=', strline)]
            temporary_ind5 = [j for j in findsubstr(temp_str + '-=', strline)]
            temporary_ind6 = [j for j in findsubstr(temp_str + '*=', strline)]
            temporary_ind7 = [j for j in findsubstr(temp_str + '%=', strline)]
            temporary_ind8 = [j for j in findsubstr(temp_str + "==", strline)]
            if len(set(temporary_ind2) - set(temporary_ind8)) > 0 or len(temporary_ind3) > 0 or len(
                    temporary_ind4) > 0 or len(temporary_ind5) > 0 or len(temporary_ind6) > 0 or len(
                temporary_ind7) > 0:
                line_features1[i - 1][15] = 1

            temporary_ind9 = [j for j in findsubstr(">=", strline)]
            temporary_ind10 = [j for j in findsubstr("<=", strline)]
            temporary_ind11 = [j for j in findsubstr(">", strline)]
            temporary_ind12 = [j for j in findsubstr("<", strline)]
            temporary_ind13 = [j for j in findsubstr("!=", strline)]
            temporary_ind14 = [j for j in findsubstr('=', strline)]
            temporary_ind15 = [j for j in findsubstr("==", strline)]
            temporary_ind16 = [j for j in findsubstr(temp_str, strline)]
            if len(temporary_ind9) > 0 or len(temporary_ind10) > 0 or len(temporary_ind11) > 0 or len(
                    temporary_ind12) > 0 or len(temporary_ind13) > 0 or len(temporary_ind15) > 0:
                if len(temporary_ind16) > 0:
                    line_features1[i - 1][16] = 1
            else:
                if len(temporary_ind14) > 0 and len(temporary_ind16) > 0:
                    for j in temporary_ind16:
                        if any(j > x for x in temporary_ind14):
                            line_features1[i - 1][16] = 1
                            break

    ###### FEATURE-18,19,20,21,...25 : COMBINATION OF FEATURE-16 AND FEATURE-17 WITH Feature-9,10,11,12(defined and being controlled by if/while/for/switch ##############
    for i in range(1, total_lines + 1):
        if line_features1[i - 1][15] == 1:
            if line_features1[i - 1][8] == 1:
                line_features1[i - 1][17] = 1
            if line_features1[i - 1][9] == 1:
                line_features1[i - 1][18] = 1
            if line_features1[i - 1][10] == 1:
                line_features1[i - 1][19] = 1
            if line_features1[i - 1][11] == 1:
                line_features1[i - 1][20] = 1
        if line_features1[i - 1][16] == 1:
            if line_features1[i - 1][8] == 1:
                line_features1[i - 1][21] = 1
            if line_features1[i - 1][9] == 1:
                line_features1[i - 1][22] = 1
            if line_features1[i - 1][10] == 1:
                line_features1[i - 1][23] = 1
            if line_features1[i - 1][11] == 1:
                line_features1[i - 1][24] = 1

    ###########  FEATURE-26 IS THE LINE CONTAINING POINTER VARIABLE DECLARATION ###############

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
                    line_features1[i - 1][25] = 1
                    if temp_var not in pointer_var_list:
                        pointer_var_list.append(temp_var)
    # print(pointer_var_list)
    # print(line_features1)

    ####  FEATURE-27 IS THE LINE INVOLVES DEFINITION OF VARIABLES FROM var_dependencylist using pointer variables ###############
    for i in range(1, total_lines + 1):
        strline = cfg_textdict[i]
        for temp_var in variables_list:
            for p_var in pointer_var_list:
                temporary_ind = [j for j in findsubstr(temp_var + '=', strline)]
                temporary_ind2 = [j for j in findsubstr(p_var, strline)]
                for j in temporary_ind:
                    for k in range(j + 2, len(strline)):
                        if k in temporary_ind2:
                            line_features1[i - 1][26] = 1
                            break

    #######   FEATURE-28,29,30,31: COMBINATION OF IF/WHILE/FOR/SWITCH FEATURES AND WHETHER THEY ARE UNDER THE CONTROL OF SOME IF/WHILE/FOR/SWITCH RESPECTIVELY #################
    for i in range(1, total_lines + 1):
        if line_features1[i - 1][1] and line_features1[i - 1][8]:
            line_features1[i - 1][27] = 1
        if line_features1[i - 1][3] and line_features1[i - 1][9]:
            line_features1[i - 1][28] = 1
        if line_features1[i - 1][5] and line_features1[i - 1][10]:
            line_features1[i - 1][29] = 1
        if line_features1[i - 1][7] and line_features1[i - 1][11]:
            line_features1[i - 1][30] = 1

    ####################### POTENTIAL LINE FEATURES ###################
    # print(potential_lines)
    potential_line_features = []
    for i in range(total_lines):
        if i + 1 in potential_lines:
            potential_line_features.append(line_features1[i])
    # print(vari, linenum)
    # print("himanshu", line_features1)
    # print( potential_line_features)

    return potential_line_features


def Sort(sub_li):
    # reverse = None (Sorts in Ascending order)
    # key is set to sort using second element of
    # sublist lambda has been used
    return (sorted(sub_li, key=lambda x: x[1], reverse=True))


def find_predicted_slice(sorted_line_scores, potential_lines):
    potential_line_size = len(potential_lines)
    max_score = sorted_line_scores[0][1]
    predicted_slice = []
    for i in range(len(sorted_line_scores)):
        if sorted_line_scores[i][1] >= max_score / 2:
            predicted_slice.append(sorted_line_scores[i][0])

    # min_predict_size = 0.3*len(sorted_line_scores)
    #  min_predict_size = int(min_predict_size)

    # if len(predicted_slice) < min_predict_size:
    #     for i in range(min_predict_size):
    #         if i < len(predicted_slice):
    #             continue
    #        else :
    #             predicted_slice.append(sorted_line_scores[i][0])

    # print("predicted slice - ", predicted_slice)

    predicted_slice.sort()
    if predicted_slice[0] == 0:
        predicted_slice.remove(0)

    # print("predicted slice - ", predicted_slice)

    return predicted_slice


def compute_inclusion_factor(actual_slice, predicted_slice):
    actual_slice_set = set(actual_slice)
    predicted_slice_set = set(predicted_slice)
    inclusion = len(actual_slice_set & predicted_slice_set)
    inclusion_factor = (inclusion * 1.0) / (len(actual_slice_set))
    return inclusion_factor


def compute_exclusion_factor(actual_slice, predicted_slice):
    actual_slice_set = set(actual_slice)
    predicted_slice_set = set(predicted_slice)
    exclusion = len(actual_slice_set.difference(predicted_slice_set))
    exclusion_factor = (exclusion * 1.0) / (len(actual_slice_set))
    return exclusion_factor


def compute_garbage_factor(actual_slice, predicted_slice):
    actual_slice_set = set(actual_slice)
    predicted_slice_set = set(predicted_slice)
    garbage = len(predicted_slice_set.difference(actual_slice_set))
    garbage_factor = (garbage * 1.0) / (len(predicted_slice_set))
    return garbage_factor


def Average(lst):
    return sum(lst) / len(lst)



def objective(w):
    test_files = []
    filesConsidered = 100
    prediction_size = 0.8
    testing_inclusion_factor = []
    testing_exclusion_factor = []
    testing_garbage_factor = []
    count_progs = 0

    for filename in os.listdir("c_prog"):
        test_files.append(filename)

    for filename in test_files:
        error_flag = 0
        count_progs += 1
        if count_progs > filesConsidered:
            break
        # print(filename)
        #print("No of files Tested ", count_progs, "/", min(filesConsidered, 3100))
        c_fileName = "c_prog/" + filename
        input_file = FileStream(c_fileName)
        lexer = CLexer(input_file)
        stream = CommonTokenStream(lexer)
        parser = CParser(stream)
        tree = parser.compilationUnit()
        # print(tree.toStringTree(recog=parser))

        # print("Start Walking...")
        cfg1 = MyCFG()
        v = MyCVisitor()
        v.visit(tree)
        # print(v.getVarList())

        v1 = MyCVisitor2(cfg1)
        v1.visit(tree)
        # print("\n\n\n", v1.getCrudeCfg())
        # vari = input("Enter a variable name: ")
        # linenum = input("Enter a line number: ")

        ###############   TOTAL LINES ##################################
        cfg_string = v1.getCrudeCfg()
        cfg_textdict = v1.getdict()
        # print("cfg_textdict :- ",cfg_textdict)
        # print("cfg_string :- ",cfg_string)

        new_cfg_string = ""
        # print("cfg_string :- ", cfg_string)
        for i in range(len(cfg_string)):
            if cfg_string[i] == '_':
                new_cfg_string += " "
            else:
                new_cfg_string += cfg_string[i]

        # print("new cfg string - ", new_cfg_string)
        cfg_string = new_cfg_string

        cfg_list = cfg_string.split(' ')

        duplicate = set()
        temp_cfg_list = []
        for i in range(len(cfg_list)):
            if cfg_list[i].isdigit():
                if cfg_list[i] not in duplicate:
                    temp_cfg_list.append(cfg_list[i])
                    duplicate.add(cfg_list[i])
            else:
                temp_cfg_list.append(cfg_list[i])
        # print(temp_cfg_list)
        # print(cfg_list)
        cfg_list = temp_cfg_list
        # print(cfg_list)
        cfg_list = [x for x in cfg_list if x != '']
        # print("cfg_list :- ",cfg_list)
        total_lines = 0
        for i in range(len(cfg_list) - 1, -1, -1):
            if cfg_list[i].isdigit():
                total_lines = int(cfg_list[i])
                break
        # print("total lines - ",total_lines)

        #############################################################3
        line_features = [[0] * 8 for i in range(0, total_lines)]
        # print(line_features)
        ######################################################################################

        ##################  ALL PREREQUISITE CALCULATIONS #####################################
        variables_list = v.getVarList()
        c_outfile = "testing_slice_module/" + filename[:-2] + ".txt"
        actual_slice_file = open(c_outfile, "r")
        # print(actual_slice_file)

        #
        actual_slice_text = actual_slice_file.read().splitlines()
        # print("actual slice text :- ",actual_slice_text)
        actual_slice_dictionary = {}
        # count1=0
        for i in actual_slice_text:
            key_value = i.split(":")
            actual_slice_dictionary[key_value[0]] = key_value[1]

        for key, value in actual_slice_dictionary.items():

            temp_str1 = ''
            temp_str2 = ''
            for i in range(2, len(key)):
                if key[i] == "'":
                    break
                else:
                    temp_str1 = temp_str1 + (key[i])
            for j in range(i + 3, len(key)):
                if key[j] == "'":
                    break
                else:
                    temp_str2 += key[j]

            vari = temp_str1
            linenum = temp_str2
            # print("variable - ",vari)
            # print("linenumber - ",linenum)

            ################################### potential_lines ###########################

            loop_info = {}
            # index_linenum = cfg_list.index('0')
            # print("index_linenum - ", index_linenum)

            for i in range(len(cfg_list)):
                if cfg_list[i] == "for" or cfg_list[i] == 'while':
                    countopen = 0

                    loop_start = int(cfg_list[i + 1])
                    last_seen_digit = loop_start
                    # print("init last seen digit - ", last_seen_digit)

                    for j in range(i + 2, len(cfg_list)):
                        if cfg_list[j] == '[':
                            countopen += 1
                        elif cfg_list[j] == ']':
                            countopen -= 1

                        elif (cfg_list[j].isdigit()) and int(cfg_list[j]) > last_seen_digit:
                            last_seen_digit = int(cfg_list[j])
                        if countopen == 0:
                            loop_info[loop_start] = last_seen_digit
                            break
            # Sort(loop_info)
            # print("loop_info - ", loop_info)

            potentialLine = int(linenum)
            for i in loop_info.keys():
                if i <= int(linenum) and loop_info[i] >= int(linenum):
                    potentialLine = max(potentialLine, loop_info[i])

            # print("PotentialLine = ",potentialLine)
            potential_lines = list(range(1, potentialLine + 1))
            # print("potential lines - ",potential_lines)

            if len(potential_lines) == 0:
                error_potential_files.append(filename)
                error_flag = 1
                break

            act_str = actual_slice_dictionary[str((vari, linenum)).replace(' ', '')]
            # print("slicing criteria - (",vari,",", linenum,")")
            # print("act_str: ",act_str)

            act_str = act_str[1:-1]
            # print("act_str: ", act_str)
            if act_str[-1] == ',':
                act_str = act_str[:-1]
            actual_slice = act_str.split(", ")

            actual_slice = [int(i) for i in actual_slice]

            if error_flag == 0:
                potential_line_scores = [0] * len(potential_lines)
                # print(potential_line_scores)
                # print("-------------d----------")
                # print(potential_lines)
                # print(cfg_textdict)
                potential_line_features = feature_calculation(vari, linenum, cfg_textdict, cfg_list, total_lines,
                                                              variables_list, potential_lines)

                line_scores = []

                last_element = potential_lines[-1]
                # print("potential lines in test file - ", potential_lines)
                # print("last element - ", last_element)
                for i in range(last_element + 10):
                    line_scores.append(-100)

                # print("len of line_features - ", len(potential_line_features))
                # print("len of line_features[0] - ", len(potential_line_features[0]))
                # print("line features : ")

                for i in range(len(potential_lines)):
                    # print("potential_line[i] = ", potential_lines[i])
                    score = 0
                    for j in range(len(w)):
                        score += potential_line_features[i][j] * w[j]
                    line_scores[potential_lines[i]] = score
                # print(" (line number,score) - ", potential_lines[i],line_scores[potential_lines[i]])

                paired_line_score = []
                # predicted_slice = []

                for i in range(len(line_scores)):
                    paired_line_score.append([i, line_scores[i]])

                sorted_line_scores = Sort(paired_line_score)
                # print("paired line score: ", sorted_line_scores)
                # print("sorted_line_score[0][0] = ",sorted_line_scores[0][1])

                # predicted_slice = find_predicted_slice(sorted_line_scores, potential_lines)

                # print("slicing criteria : ", linenum, vari)
                # print("predicted slice = ", predicted_slice)
                # print("actual slice = ", actual_slice)

                # for i in range(len(predicted_slice)):
                # print("score - ", sorted_line_scores[i][1], " line - ",sorted_line_scores[i][0])

                prediction_len = prediction_size * potentialLine
                predicted_slice = []
                for i in range(int(prediction_len + 0.5)):
                    predicted_slice.append(sorted_line_scores[i][0])

                if linenum not in predicted_slice:
                    predicted_slice.append(int(linenum))
                # print("actual slice - ",actual_slice)
                predicted_slice.sort()
                # print("predicted slice - ",predicted_slice)

                inclusion_factor = compute_inclusion_factor(actual_slice, predicted_slice)
                exclusion_factor = compute_exclusion_factor(actual_slice, predicted_slice)
                garbage_factor = compute_garbage_factor(actual_slice, predicted_slice)

                # print("Inclusion factor - ", inclusion_factor)
                testing_inclusion_factor.append(inclusion_factor)
                testing_exclusion_factor.append(exclusion_factor)
                testing_garbage_factor.append(garbage_factor)

    overall_testing_inclusion_factor = Average(testing_inclusion_factor)
    #print("Overall Testing inclusion factor = ", overall_testing_inclusion_factor, " at ",
          #prediction_size * 100, "% line inclusion")

    overall_testing_exclusion_factor = Average(testing_exclusion_factor)
    #print("Overall Testing exclusion factor = ", overall_testing_exclusion_factor, " at ",
          #prediction_size * 100,
          #"% line inclusion")

    overall_testing_garbage_factor = Average(testing_garbage_factor)
    #print("Overall Testing garbage factor = ", overall_testing_garbage_factor, " at ", prediction_size * 100,
          #"% line inclusion")

    return (-1)*(overall_testing_exclusion_factor + overall_testing_garbage_factor)


# surrogate or approximation for the objective function
def surrogate(model, X):
    # catch any warning generated when making a prediction
    with catch_warnings():
        # ignore generated warnings
        simplefilter("ignore")
        return model.predict(X, return_std=True)


# probability of improvement acquisition function
def acquisition(X, Xsamples, model):
    # calculate the best surrogate score found so far
    yhat, _ = surrogate(model, X)
    best = max(yhat)
    #print("yhat - ", yhat)
    #print("_ = ", _)
    # calculate mean and stdev via surrogate function
    mu, std = surrogate(model, Xsamples)
    mu = mu[:, 0]
    # calculate the probability of improvement
    probs = norm.cdf((mu - best) / (std + 1E-9))
    return probs


# optimize the acquisition function
def opt_acquisition(X, y, model):
    # random search, generate random samples
    Xsamples = asarray([random.uniform(-1,1) for i in range(0,100)])
    Xsamples = Xsamples.reshape(len(Xsamples), 1)
    # calculate the acquisition function for each sample
    scores = acquisition(X, Xsamples, model)
    # locate the index of the largest scores
    ix = argmax(scores)
    return Xsamples[ix, 0]


# plot real observations vs surrogate function
def plot(X, y, model):
    # scatter plot of inputs and real objective function
    pyplot.scatter(X, y)
    # line plot of surrogate function across domain
    Xsamples = asarray(arange(0, 1, 0.001))
    Xsamples = Xsamples.reshape(len(Xsamples), 1)
    ysamples, _ = surrogate(model, Xsamples)
    pyplot.plot(Xsamples, ysamples)
    # show the plot
    pyplot.show()


def bayesianOptimisation(X, y, hyperparameter, index):

    X = X.reshape(len(X), 1)
    y = y.reshape(len(y), 1)
    model = GaussianProcessRegressor()
    model.fit(X, y)
    #plot(X, y, model)

    number_of_optimisation_steps = 30

    for i in range(number_of_optimisation_steps):
        x = opt_acquisition(X, y, model)
        #print("optimal acquisition for x[",index,"] = ", x)
        #
        #       CHOOSE THE HYPERPARAMETER VIA SOME STRATEGY
        #

        #   TRYING TO LOOK FOR OPTIMAL X , WITH PREVIOUS KNOWLEDGE
        if i < number_of_optimisation_steps/2 :
            w = hyperparameter
            w[index] = x
            actual = objective(w)

        #   RANDOMISING THE SEARCH SPACE, TO AVOID LOCAL MINIMAS
        else :
            w = []
            for i in range(29):
                w.append(random.uniform(-1, 1))
            w[index] = x
            actual = objective(w)

        # summarize the finding
        est, _ = surrogate(model, [[x]])
        #print('>x=%.3f, f()=%3f, actual=%.3f' % (x, est, actual))
        # add the data to the dataset
        X = vstack((X, [[x]]))
        y = vstack((y, [[actual]]))
        # update the model
        model.fit(X, y)

    ix = argmax(y)
    print('Best Result: x=%.3f, y=%.3f' % (X[ix], y[ix]))
    return X[ix], y[ix]



def main():
    print("")

    hyperparameter = []
    number_of_random_searches = 100
    number_of_features = 29

    w = [0.78698881, -0.99695, 0.60753981, 0.93986908, 0.97150144, 0.99835333, -0.9707696, 0.91335105, -0.80650674, -0.9843982, -0.46083039, 0.98005665, -0.82679469,
         -0.99460156, 0.47607437, 0.84021445, 0.30782409, 0.66125245, 0.20495883, -0.00796212, -0.70300896, 0.57139532, -0.76471305, 0.2516651, 0.61799571, 0.99102757,
         -0.74334154, 0.35878196, -0.32411694]

    hyperparameter.append(w)

    for i in range(number_of_random_searches-1):
        w = []
        for i in range(number_of_features):
            w.append(random.uniform(-1, 1))
        hyperparameter.append(w)
    # print("w = ", i, w[i])
    y = asarray([objective(x) for x in hyperparameter])

    bestScore = -2
    bestparameter = []

    for i in range(number_of_random_searches):
        if y[i] > bestScore :
            bestparameter.append(hyperparameter[i])
            bestScore = y[i]


    print("Bestparameter - ", bestparameter[-1])
    print("Best score - ", bestScore)
    #a = input()

    Y_scores = []
    bestHyperparameter = []

    constructed_hyperparameter = bestparameter[-1]
    ####################    GENERATED 100 pairs of hyperparameter w and the corresponding objective value


    X_zero = asarray([hyperparameter[x][0] for x in range(number_of_random_searches)])
    X_res, Y_res = bayesianOptimisation(X_zero, y, constructed_hyperparameter, 0)
    bestHyperparameter.append(X_res)
    Y_scores.append(Y_res)
    constructed_hyperparameter[0] = X_res

    X_one = asarray([hyperparameter[x][1] for x in range(number_of_random_searches)])
    X_res, Y_res = bayesianOptimisation(X_one, y, constructed_hyperparameter, 1)
    bestHyperparameter.append(X_res)
    Y_scores.append(Y_res)
    constructed_hyperparameter[1] = X_res

    X_two = asarray([hyperparameter[x][2] for x in range(number_of_random_searches)])
    X_res, Y_res = bayesianOptimisation(X_two, y, constructed_hyperparameter, 2)
    bestHyperparameter.append(X_res)
    Y_scores.append(Y_res)
    constructed_hyperparameter[2] = X_res

    X_three = asarray([hyperparameter[x][3] for x in range(number_of_random_searches)])
    X_res, Y_res = bayesianOptimisation(X_three, y, constructed_hyperparameter, 3)
    bestHyperparameter.append(X_res)
    Y_scores.append(Y_res)
    constructed_hyperparameter[3] = X_res


    X_four = asarray([hyperparameter[x][4] for x in range(number_of_random_searches)])
    X_res, Y_res = bayesianOptimisation(X_four, y, constructed_hyperparameter, 4)
    bestHyperparameter.append(X_res)
    Y_scores.append(Y_res)
    constructed_hyperparameter[4] = X_res

    X_five = asarray([hyperparameter[x][5] for x in range(number_of_random_searches)])
    X_res, Y_res = bayesianOptimisation(X_five, y, constructed_hyperparameter, 5)
    bestHyperparameter.append(X_res)
    Y_scores.append(Y_res)
    constructed_hyperparameter[5] = X_res

    X_six = asarray([hyperparameter[x][6] for x in range(number_of_random_searches)])
    X_res, Y_res = bayesianOptimisation(X_six, y, constructed_hyperparameter, 6)
    bestHyperparameter.append(X_res)
    Y_scores.append(Y_res)
    constructed_hyperparameter[6] = X_res

    X_seven = asarray([hyperparameter[x][7] for x in range(number_of_random_searches)])
    X_res, Y_res = bayesianOptimisation(X_seven, y, constructed_hyperparameter, 7)
    bestHyperparameter.append(X_res)
    Y_scores.append(Y_res)
    constructed_hyperparameter[7] = X_res

    X_eight = asarray([hyperparameter[x][8] for x in range(number_of_random_searches)])
    X_res, Y_res = bayesianOptimisation(X_eight, y, constructed_hyperparameter, 8)
    bestHyperparameter.append(X_res)
    Y_scores.append(Y_res)
    constructed_hyperparameter[8] = X_res

    X_nine = asarray([hyperparameter[x][9] for x in range(number_of_random_searches)])
    X_res, Y_res = bayesianOptimisation(X_nine, y, constructed_hyperparameter, 9)
    bestHyperparameter.append(X_res)
    Y_scores.append(Y_res)
    constructed_hyperparameter[9] = X_res


    X_ten = asarray([hyperparameter[x][10] for x in range(number_of_random_searches)])
    X_res, Y_res = bayesianOptimisation(X_ten, y, constructed_hyperparameter, 10)
    bestHyperparameter.append(X_res)
    Y_scores.append(Y_res)
    constructed_hyperparameter[10] = X_res

    X_eleven = asarray([hyperparameter[x][11] for x in range(number_of_random_searches)])
    X_res, Y_res = bayesianOptimisation(X_eleven, y, constructed_hyperparameter, 11)
    bestHyperparameter.append(X_res)
    Y_scores.append(Y_res)
    constructed_hyperparameter[11] = X_res

    X_twelve = asarray([hyperparameter[x][12] for x in range(number_of_random_searches)])
    X_res, Y_res = bayesianOptimisation(X_twelve, y, constructed_hyperparameter, 12)
    bestHyperparameter.append(X_res)
    Y_scores.append(Y_res)
    constructed_hyperparameter[12] = X_res

    X_thirteen = asarray([hyperparameter[x][13] for x in range(number_of_random_searches)])
    X_res, Y_res = bayesianOptimisation(X_thirteen, y, constructed_hyperparameter, 13)
    bestHyperparameter.append(X_res)
    Y_scores.append(Y_res)
    constructed_hyperparameter[13] = X_res

    X_fourteen = asarray([hyperparameter[x][14] for x in range(number_of_random_searches)])
    X_res, Y_res = bayesianOptimisation(X_fourteen, y, constructed_hyperparameter, 14)
    bestHyperparameter.append(X_res)
    Y_scores.append(Y_res)
    constructed_hyperparameter[14] = X_res

    X_fifteen = asarray([hyperparameter[x][15] for x in range(number_of_random_searches)])
    X_res, Y_res = bayesianOptimisation(X_fifteen, y, constructed_hyperparameter, 15)
    bestHyperparameter.append(X_res)
    Y_scores.append(Y_res)
    constructed_hyperparameter[15] = X_res

    X_sixteen = asarray([hyperparameter[x][16] for x in range(number_of_random_searches)])
    X_res, Y_res = bayesianOptimisation(X_sixteen, y, constructed_hyperparameter, 16)
    bestHyperparameter.append(X_res)
    Y_scores.append(Y_res)
    constructed_hyperparameter[16] = X_res

    X_seventeen = asarray([hyperparameter[x][17] for x in range(number_of_random_searches)])
    X_res, Y_res = bayesianOptimisation(X_seventeen, y, constructed_hyperparameter, 17)
    bestHyperparameter.append(X_res)
    Y_scores.append(Y_res)
    constructed_hyperparameter[17] = X_res

    X_eighteen = asarray([hyperparameter[x][18] for x in range(number_of_random_searches)])
    X_res, Y_res = bayesianOptimisation(X_eighteen, y, constructed_hyperparameter, 18)
    bestHyperparameter.append(X_res)
    Y_scores.append(Y_res)
    constructed_hyperparameter[18] = X_res

    X_nineteen = asarray([hyperparameter[x][19] for x in range(number_of_random_searches)])
    X_res, Y_res = bayesianOptimisation(X_nineteen, y, constructed_hyperparameter, 19)
    bestHyperparameter.append(X_res)
    Y_scores.append(Y_res)
    constructed_hyperparameter[19] = X_res

    X_twenty = asarray([hyperparameter[x][20] for x in range(number_of_random_searches)])
    X_res, Y_res = bayesianOptimisation(X_twenty, y, constructed_hyperparameter, 20)
    bestHyperparameter.append(X_res)
    Y_scores.append(Y_res)
    constructed_hyperparameter[20] = X_res

    X_twentyone = asarray([hyperparameter[x][21] for x in range(number_of_random_searches)])
    X_res, Y_res = bayesianOptimisation(X_twentyone, y, constructed_hyperparameter, 21)
    bestHyperparameter.append(X_res)
    Y_scores.append(Y_res)
    constructed_hyperparameter[21] = X_res

    X_twentytwo = asarray([hyperparameter[x][22] for x in range(number_of_random_searches)])
    X_res, Y_res = bayesianOptimisation(X_twentytwo, y, constructed_hyperparameter, 22)
    bestHyperparameter.append(X_res)
    Y_scores.append(Y_res)
    constructed_hyperparameter[22] = X_res

    X_twentythree = asarray([hyperparameter[x][23] for x in range(number_of_random_searches)])
    X_res, Y_res = bayesianOptimisation(X_twentythree, y, constructed_hyperparameter, 23)
    bestHyperparameter.append(X_res)
    Y_scores.append(Y_res)
    constructed_hyperparameter[23] = X_res

    X_twentyfour = asarray([hyperparameter[x][24] for x in range(number_of_random_searches)])
    X_res, Y_res = bayesianOptimisation(X_twentyfour, y, constructed_hyperparameter, 24)
    bestHyperparameter.append(X_res)
    Y_scores.append(Y_res)
    constructed_hyperparameter[24] = X_res

    X_twentyfive = asarray([hyperparameter[x][25] for x in range(number_of_random_searches)])
    X_res, Y_res = bayesianOptimisation(X_twentyfive, y, constructed_hyperparameter, 25)
    bestHyperparameter.append(X_res)
    Y_scores.append(Y_res)
    constructed_hyperparameter[25] = X_res

    X_twentysix = asarray([hyperparameter[x][26] for x in range(number_of_random_searches)])
    X_res, Y_res = bayesianOptimisation(X_twentysix, y, constructed_hyperparameter, 26)
    bestHyperparameter.append(X_res)
    Y_scores.append(Y_res)
    constructed_hyperparameter[26] = X_res

    X_twentyseven = asarray([hyperparameter[x][27] for x in range(number_of_random_searches)])
    X_res, Y_res = bayesianOptimisation(X_twentyseven, y, constructed_hyperparameter, 27)
    bestHyperparameter.append(X_res)
    Y_scores.append(Y_res)
    constructed_hyperparameter[27] = X_res

    X_twentyeight = asarray([hyperparameter[x][28] for x in range(number_of_random_searches)])
    X_res, Y_res = bayesianOptimisation(X_twentyeight, y, constructed_hyperparameter, 28)
    bestHyperparameter.append(X_res)
    Y_scores.append(Y_res)
    constructed_hyperparameter[28] = X_res


    print("bestHyperparameter - ", bestHyperparameter)
    print("")
    print("best score - ", Y_scores)

    print("")
    print("should be optimal hyperparameter - ", constructed_hyperparameter)
    print("Obtained score - ", objective(constructed_hyperparameter))


if __name__ == '__main__':
    main()
