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
import time
from Chelper import MyHelper
from Cutility import MyUtility
from DefSetVisitor import DefSetVisitor
from UseSetVisitor import UseSetVisitor

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
            #print("appending variable - ", ctx.getText())

        elif ctx.getChildCount()==4:
            #print("array variable - ", ctx.children[0].children[0].getText())
            self.VarList.append(ctx.children[0].children[0].getText()+"_arr")



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
        #print("crude_cfg - ", self.crude_cfg)
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
                print(self.nodeCounter, "\n", ctx.children[1].children[0].children[1].children[0].children[2].getText())  # function params     <------node
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
                print(self.nodeCounter, "\n", ctx.children[0].children[0].children[1].children[0].children[2].getText())  # function params     <------node
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
            else:                                                           # no need to create node for else block in case of simple if statements
                node = MyNode(self.noElse,None)
                self.cfg.addNode(node)
                self.crude_cfg = self.crude_cfg + str(self.noElse)
                self.noElse = self.noElse-1
            ############# no else part ##############
            self.crude_cfg = self.crude_cfg + " ] "
            self.crude_cfg = self.crude_cfg + " ] "
        if (str(ctx.children[0]) == "switch"):   # switch statement not working properly
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


def findall(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]


def feature_calculation(variable,linenumber,cfg_textdict,cfg_list,total_lines,variables_list,potential_lines):
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
    #print(potential_lines)
    potential_line_features = []
    for i in range(total_lines):
        if i + 1 in potential_lines:
            potential_line_features.append(line_features1[i])
    #print(vari, linenum)
    #print("himanshu", line_features1)
    #print( potential_line_features)

    return potential_line_features


def feature_reward( line_features, max_linenum, label):
    number_of_features = 31
    full_reward=2
    full_penalty = 2
    semi_reward=1
    semi_penalty=1

    w = [0 for i in range(number_of_features)]
    for i in range(0, max_linenum-1):

        if label[i]==-1:
            continue
        elif label[i]==1:
            for j in range(0, number_of_features):
                if line_features[i][j]==1:
                    w[j]+=full_reward
                else:
                    w[j]-=semi_penalty
        else:
            for j in range(0, number_of_features):
                if line_features[i][j]==1:
                    w[j]-=full_penalty
                else:
                    w[j]+=semi_reward

    #print("Hyperparameter vector(w): ",w)
    return w

def centroid_hyperparameter(w):
    optimal_hyperparameter = []

    number_of_hyperparameters = len(w)
    for i in range(31):
        val = 0
        for j in range(number_of_hyperparameters):
            val += w[j][i]
        val = val / number_of_hyperparameters
        optimal_hyperparameter.append(val)

    return optimal_hyperparameter


def Sort(sub_li):
    # reverse = None (Sorts in Ascending order)
    # key is set to sort using second element of
    # sublist lambda has been used
    return (sorted(sub_li, key=lambda x: x[1],reverse = True))


def find_predicted_slice(sorted_line_scores, potential_lines):

    potential_line_size = len(potential_lines)
    max_score = sorted_line_scores[0][1]
    predicted_slice = []
    for i in range( len(sorted_line_scores) ):
        if sorted_line_scores[i][1]>=max_score/2:
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


def compute_inclusion_factor(actual_slice,predicted_slice):
    actual_slice_set = set(actual_slice)
    predicted_slice_set = set(predicted_slice)
    inclusion = len(actual_slice_set & predicted_slice_set)
    inclusion_factor = (inclusion*1.0)/(len(actual_slice_set))
    return inclusion_factor

def compute_exclusion_factor(actual_slice,predicted_slice):
    actual_slice_set = set(actual_slice)
    predicted_slice_set = set(predicted_slice)
    exclusion = len(actual_slice_set.difference(predicted_slice_set))
    exclusion_factor = (exclusion*1.0)/(len(actual_slice_set))
    return exclusion_factor

def compute_garbage_factor(actual_slice,predicted_slice):
    actual_slice_set = set(actual_slice)
    predicted_slice_set = set(predicted_slice)
    garbage = len(predicted_slice_set.difference(actual_slice_set))
    garbage_factor = (garbage*1.0)/(len(predicted_slice_set))
    return garbage_factor

def Average(lst):
    return sum(lst) / len(lst)



def main():

    # ******************        TRAINING        *************************

    # for files in c_prog_slice_half
    ######## for actual_slices in file.txt
    #        # extract the slicing criteria
    #        # store the actual slice wrt the slicing criteria in a list
    #        # Make a list named label from the actual slice information
    #        # Open file.c , and extract the required information given below
    #        # Find the potential lines wrt the slicing criteria
    #        # Extract the features of the potential lines wrt the slicing criteria
    #        # Make a call to the function feature_reward, and keep on storing the optimal hyperparameters in a global list

    w = []
    files = []
    count_progs=0


    prediction_size = 0.8
    filesConsidered = 6500

    training_inclusion_factor = []
    training_exclusion_factor = []
    training_garbage_factor = []

    error_slice_files = []
    error_potential_files = []
    error_flag=0


    training_files = []
    test_files = []

    for filename in os.listdir("c_prog"):
        files.append(filename)

    train_size = 0.8*len(files)

    for i in range(len(files)):
        if i<= train_size:
            training_files.append(files[i])
        else:
            test_files.append(files[i])

    #print("Number of files - ", len(files))
    #print("Number of training files - ",len(training_files))
    #print("Number of test files - ", len(test_files))

    for filename in training_files:
        count_progs+=1
        if count_progs > filesConsidered:
            break
        error_flag=0
        #print(filename)
        print("No of files Trained ",count_progs,"/",filesConsidered)
        c_fileName = "c_prog/"+filename
        input_file = FileStream(c_fileName)
        lexer = CLexer(input_file)
        stream = CommonTokenStream(lexer)
        parser = CParser(stream)
        tree = parser.compilationUnit()
        #print(tree.toStringTree(recog=parser))


        #print("Start Walking...")
        cfg1 = MyCFG()
        v = MyCVisitor()
        v.visit(tree)
        #print("Variable list - ",v.getVarList())

        v1 = MyCVisitor2(cfg1)
        v1.visit(tree)

        # v2 = MyCVisitor2()
        # v2.visit(tree)
        #print("\n\n\n", v1.getCrudeCfg())
        #vari = input("Enter a variable name: ")
        #linenum = input("Enter a line number: ")

        ###############   TOTAL LINES ##################################
        cfg_string = v1.getCrudeCfg()
        cfg_textdict = v1.getdict()
        #print("cfg_textdict :- ",cfg_textdict)
        new_cfg_string = ""
        #print("cfg_string :- ",cfg_string)
        for i in range(len(cfg_string)):
            if cfg_string[i]=='_' :
                new_cfg_string += " "
            else :
                new_cfg_string += cfg_string[i]

        duplicate = set()

        #print("new cfg string - ",new_cfg_string)
        cfg_string = new_cfg_string
        cfg_list = cfg_string.split(' ')
        temp_cfg_list = []

        for i in range(len(cfg_list)):
            if cfg_list[i].isdigit():
                if cfg_list[i] not in duplicate:
                    temp_cfg_list.append(cfg_list[i])
                    duplicate.add(cfg_list[i])
            else:
                temp_cfg_list.append(cfg_list[i])
        #print(temp_cfg_list)
        #print(cfg_list)
        cfg_list = temp_cfg_list
        cfg_list = [x for x in cfg_list if x != '']
        #print("cfg_list :- ",cfg_list)
        total_lines = 0
        for i in range(len(cfg_list) - 1, -1, -1):
            if cfg_list[i].isdigit():
                total_lines = int(cfg_list[i])
                break
        #print("total lines - ",total_lines)

        #############################################################3
        line_features = [[0] * 8 for i in range(0,total_lines)]
        #print(line_features)
     ######################################################################################

    ##################  ALL PREREQUISITE CALCULATIONS #####################################
        variables_list = v.getVarList()
        c_outfile = "testing_slice_module/" + filename[:-2]+".txt"
        actual_slice_file = open(c_outfile, "r")
        # print(actual_slice_file)

        #
        actual_slice_text = actual_slice_file.read().splitlines()
        #print("actual slice text :- ",actual_slice_text)
        actual_slice_dictionary = {}
        #count1=0
        for i in actual_slice_text:
            key_value = i.split(":")
            actual_slice_dictionary[key_value[0]] = key_value[1]

        for key, value in actual_slice_dictionary.items():

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

            vari = temp_str1
            linenum=temp_str2
            #print("variable - ",vari)
            #print("linenumber - ",linenum)

            ################################### potential_lines ###########################

            loop_info = {}
            #index_linenum = cfg_list.index('0')
            #print("index_linenum - ", index_linenum)

            for i in range(len(cfg_list)):
                if cfg_list[i] == "for" or cfg_list[i] == 'while':
                    countopen = 0

                    loop_start = int(cfg_list[i+1])
                    last_seen_digit = loop_start
                    #print("init last seen digit - ", last_seen_digit)

                    for j in range(i+2,len(cfg_list)):
                        if cfg_list[j] == '[':
                            countopen += 1
                        elif cfg_list[j] == ']':
                            countopen -= 1

                        elif (cfg_list[j].isdigit()) and int(cfg_list[j]) > last_seen_digit:
                            last_seen_digit = int(cfg_list[j])
                        if countopen == 0:
                            loop_info[loop_start] = last_seen_digit
                            break
            #Sort(loop_info)
            #print("loop_info - ", loop_info)

            potentialLine = int(linenum)
            for i in loop_info.keys():
                if i <= int(linenum) and loop_info[i] >= int(linenum) :
                    potentialLine = max(potentialLine, loop_info[i])

            #print("PotentialLine = ",potentialLine)
            potential_lines = list(range(1, potentialLine+1))
            #print("potential lines - ",potential_lines)


            if len(potential_lines) == 0:
                error_potential_files.append(filename)
                error_flag=1
                break


            max_linenum = potential_lines[-1]

            if max_linenum < int(linenum):
                max_linenum = int(linenum)

            #print("max_linenum - ", max_linenum)
            label = []
            for i in range(max_linenum+10):
                label.append(-1)

            #print("label - ",label)

            #print("last line number under consideration: ", max_linenum)
            act_str = actual_slice_dictionary[str((vari, linenum)).replace(' ', '')]
            #print("slicing criteria - (",vari,",", linenum,")")
            #print("act_str = ",act_str)
            #print("act_str: ",act_str)

            act_str = act_str[1:-1]
            if act_str[-1] == ',':
                act_str = act_str[:-1]
            #print("act_str: ", act_str)
            actual_slice = act_str.split(", ")

            #print("actual slice - ",actual_slice)
            actual_slice=[int(i) for i in actual_slice]

            #print("actual slice: ",actual_slice)

            for i in range(len(potential_lines)):
                #print("label(",potential_lines[i]-1,") is accessed in potential lines....")
                label[potential_lines[i]-1] = 0

            for i in range(len(actual_slice)):
                if actual_slice[i-1] > max_linenum:
                    #print("label(", actual_slice[i - 1], ") is accessed in actual slice....")
                    #print("potential lines - ", potential_lines)
                    #print("error!!!", max_linenum)
                    print("###########")
                    print("Potential Line - ",potentialLine)
                    print("Potential lines - ",potential_lines)
                    print("actual slice - ", actual_slice)
                    print("slicing criteria - ", linenum, " ",vari)
                    print("loop info - ",loop_info)
                    print("#################")
                    error_slice_files.append(filename)
                    error_flag=1
                    break
                else:
                    label[actual_slice[i-1]] = 1

            #print("label - ",label)


            #################################       LABEL       ##############################
            #   label consists of 3 values , 0 for the lines which are not present in the actual slice
            #   1 for the lines which are present in the actual slice
            #   -1 for the lines which are not the potential lines itself (like the linenum)

            if error_flag==0:
                potential_line_scores = [0] * len(potential_lines)
                #print(potential_line_scores)
                #print("-------------d----------")
                #print(potential_lines)
                #print(cfg_textdict)
                potential_line_features = feature_calculation(vari,linenum,cfg_textdict,cfg_list,total_lines,variables_list,potential_lines)

                #print("potential line features : ",potential_line_features)
                # print("length of potential line features: ",len(potential_line_features))

                temp_w = feature_reward(potential_line_features, max_linenum, label)
                w.append(temp_w)
                #print("hyperparameter : ",w)
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
                    for j in range(len(temp_w)):
                        score += potential_line_features[i][j] * temp_w[j]
                    line_scores[potential_lines[i]] = score
                    # print(" (line number,score) - ", potential_lines[i],line_scores[potential_lines[i]])

                paired_line_score = []


                for i in range(len(line_scores)):
                    paired_line_score.append([i, line_scores[i]])

                sorted_line_scores = Sort(paired_line_score)
                # print("paired line score: ", sorted_line_scores)
                # print("sorted_line_score[0][0] = ",sorted_line_scores[0][1])
                #for i in range(len(potential_lines)):
                    #print("score - ", sorted_line_scores[i][1], " line - ",sorted_line_scores[i][0])



                prediction_len = prediction_size * potentialLine
                predicted_slice = []
                for i in range(int(prediction_len+0.5)):
                    predicted_slice.append(sorted_line_scores[i][0])

                if linenum not in predicted_slice:
                    predicted_slice.append(int(linenum))
                #print("actual slice - ",actual_slice)
                predicted_slice.sort()
                #print("predicted slice - ",predicted_slice)

                inclusion_factor = compute_inclusion_factor(actual_slice,predicted_slice)
                exclusion_factor = compute_exclusion_factor(actual_slice,predicted_slice)
                garbage_factor = compute_garbage_factor(actual_slice,predicted_slice)

                #print("Inclusion factor - ", inclusion_factor)
                training_inclusion_factor.append(inclusion_factor)
                training_exclusion_factor.append(exclusion_factor)
                training_garbage_factor.append(garbage_factor)


    #print("Hyperparameter w : ", w)
    #print("number of hyperparameters: ", len(w))

    #centroid_w = []
    optimal_w = centroid_hyperparameter(w)

    print("optimal hyperparameter: - ", optimal_w)

    print("Number of error slice files = ", len(error_slice_files))
    print("error files - ",error_slice_files)
    print("Number of error potential line files = ", len(error_potential_files))

    write_file = open("error_filenames.txt", 'w')

    for i in range(len(error_slice_files)):
        write_file.writelines(error_slice_files[i])
        write_file.writelines("\n")

    write_file.close()
    #a = input()
    # From the list of the optimal hyperparameters, find the representative point ( mean, centroid, mode etc...)


    # ******************        TESTING          **************************

    # From the slicing criteria, calculate the potential lines
    # Extract the features of the potential lines wrt the slicing criteria
    # Multiply the feature vectors with the calculated most optimal hyperparameter 'w'
    # Sort the potential lines based on the above calculated scores
    # Use a strategy to select 'k' top lines in the descending order


    # optimal_w = [6.781570994042934, 8.846204678192084, 12.017424176165903, 11.621459043954015, 12.343886961507438, 12.198380999582131, 11.441464291614434, 11.441464291614434, -3.4827944763515153,
    #              -7.6927300467430495, -4.1275278660486086, 11.441464291614434, 11.02106838478956, 11.269836642274763, 11.224065381961653, 7.896815447557408, 3.779676005558633, 8.565979611867487, 8.666851306570265, 10.166370271031942, 11.441464291614434,
    #              6.697346044333012, 6.046927689183017, 7.403739443942354, 11.441464291614434, 11.343624578486535, 11.303917281323187, 10.089200509217418, 11.483533035965909, 11.30995209080396, 11.441464291614434]


    print("***************************  TESTING  ***********************************")

    testing_inclusion_factor = []
    testing_exclusion_factor = []
    testing_garbage_factor = []
    count_progs=0

    for filename in test_files:
        error_flag = 0
        count_progs+=1
        if count_progs> filesConsidered:
            break
        #print(filename)
        print("No of files Tested ", count_progs, "/",min(filesConsidered,3100))
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
        #print("cfg_string :- ", cfg_string)
        for i in range(len(cfg_string)):
            if cfg_string[i] == '_':
                new_cfg_string += " "
            else:
                new_cfg_string += cfg_string[i]

        #print("new cfg string - ", new_cfg_string)
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
        #print(temp_cfg_list)
        #print(cfg_list)
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
                #print("potential lines in test file - ", potential_lines)
                #print("last element - ", last_element)
                for i in range(last_element+10):
                    line_scores.append(-100)

                #print("len of line_features - ", len(potential_line_features))
                #print("len of line_features[0] - ", len(potential_line_features[0]))
                #print("line features : ")

                for i in range(len(potential_lines)):
                    #print("potential_line[i] = ", potential_lines[i])
                    score = 0
                    for j in range(len(optimal_w)):
                        score += potential_line_features[i][j]*optimal_w[j]
                    line_scores[potential_lines[i]]  = score
                    #print(" (line number,score) - ", potential_lines[i],line_scores[potential_lines[i]])


                paired_line_score = []
                #predicted_slice = []

                for i in range(len(line_scores)):
                    paired_line_score.append([i, line_scores[i]])

                sorted_line_scores = Sort(paired_line_score)
                #print("paired line score: ", sorted_line_scores)
                #print("sorted_line_score[0][0] = ",sorted_line_scores[0][1])

                #predicted_slice = find_predicted_slice(sorted_line_scores, potential_lines)

                #print("slicing criteria : ", linenum, vari)
                #print("predicted slice = ", predicted_slice)
                #print("actual slice = ", actual_slice)

                #for i in range(len(predicted_slice)):
                    #print("score - ", sorted_line_scores[i][1], " line - ",sorted_line_scores[i][0])

                #prediction_size = 0.7
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


    print("Files considered - ",filesConsidered)

    overall_training_inclusion_factor = Average(training_inclusion_factor)
    print("Overall Training inclusion factor = ", overall_training_inclusion_factor, " at ", prediction_size * 100,
          "% line inclusion")

    overall_training_exclusion_factor = Average(training_exclusion_factor)
    print("Overall Training exclusion factor = ", overall_training_exclusion_factor, " at ", prediction_size * 100,
          "% line inclusion")

    overall_training_garbage_factor = Average(training_garbage_factor)
    print("Overall Training garbage factor = ", overall_training_garbage_factor, " at ", prediction_size * 100,
          "% line inclusion")

    overall_testing_inclusion_factor = Average(testing_inclusion_factor)
    print("Overall Testing inclusion factor = ", overall_testing_inclusion_factor, " at ",
                  prediction_size * 100, "% line inclusion")

    overall_testing_exclusion_factor = Average(testing_exclusion_factor)
    print("Overall Testing exclusion factor = ", overall_testing_exclusion_factor, " at ",
                  prediction_size * 100,
                  "% line inclusion")

    overall_testing_garbage_factor = Average(testing_garbage_factor)
    print("Overall Testing garbage factor = ", overall_testing_garbage_factor, " at ", prediction_size * 100,
                  "% line inclusion")








    ######################      add the logic to compute line scores and predict the slice      #################

                # print("potential line features : ",potential_line_features)
                # print("length of potential line features: ",len(potential_line_features))


                # print("hyperparameter : ",w)

    # ******************        ACCURACY OF THE M0DEL       **********************

    # Make a call to the function measure_accuracy to find the inclusion, exclusion and garbage factor given that the actual slice is known

if __name__ == '__main__':
    main()