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
                print(self.nodeCounter, "\n", ctx.children[1].children[0].children[1].children[0].children[2].getText())  # function params     <------node
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




def main():

    #####################  INITIALIZATION #####################################################################
    inclusion_factor_overall = 0.0
    redundancy_factor_overall=0.0
    optimal_factors_overall = (inclusion_factor_overall,redundancy_factor_overall)
    files = []
    w = []
    for i in range(0, 31):
        w.append(random.uniform(-1, 1))
    print("w - ",w)
    wmax = w
    count_progs=0
    for filename in os.listdir("c_prog"):
        files.append(filename)
        count_progs+=1
        if count_progs == 2:
            break
        # if count_progs==2 or count_progs==21:
        #     continue
        print(count_progs)
        print(filename)
        c_fileName = "c_prog/"+filename
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

        v1 = MyCVisitor2()
        v1.visit(tree)
        #print("\n\n\n", v1.getCrudeCfg())
        #vari = input("Enter a variable name: ")
        #linenum = input("Enter a line number: ")







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
        line_features = [[0] * 8 for i in range(0,total_lines)]
        # print(line_features)


























     ######################################################################################



    ##################  ALL PREREQUISITE CALCULATIONS #####################################
        variables_list = v.getVarList()
        c_outfile = "c_prog_slice_half/" + filename[:-2]+".txt"
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
        #print(actual_slice_dictionary)
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

                    if cfg_list[i - 2] == "while" or cfg_list[i-2]=="for":
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
                #print("-------------c----------")


            #print("-------------A----------")
            #print(potential_lines)
            act_str = actual_slice_dictionary[str((vari, linenum)).replace(' ', '')]
            #print(vari, linenum)
            #print(act_str)



            ########################### RANDOM SAMPLING ALGORITHM FOR CODE-BASE #######################################


            potential_line_scores = [0] * len(potential_lines)
            #print("potential line score - ",potential_line_scores)
            #print("-------------d----------")
            #print(potential_lines)
            #print(cfg_textdict)
            potential_line_features = feature_calculation(vari,linenum,cfg_textdict,cfg_list,total_lines,variables_list,potential_lines)
            #print("potential line features - ",potential_line_features)
            #print("-------------e-----------")

            #enumerate through the potential lines
            k = 0
            for i in range(len(potential_line_scores)):
                # line_scores.append(0)
                k+=1
                for j in range(len(w)):
                    #if k<2:
                        #print("w[",j,"] - ",w[j])
                    potential_line_scores[i] = potential_line_scores[i] + (w[j] * potential_line_features[i][j])
                    #if k<2 and potential_line_features[i][j]>0:
                        #print("potential_line_scores[", i, "] - ", potential_line_scores[i])
            #print(potential_lines)
            #print("features[5] - ", potential_line_features[5])
            #print("w - ",w)
            #print("score[5] - ",potential_line_scores[5])
            #print(potential_line_scores)
            #print("-------------f----------")
            #print(len(potential_lines))
            if len(potential_lines)>20:
                continue
            abstraction_scores = [0] * (2 ** (len(potential_lines)))
            allsubsets = lambda n: list(itertools.chain(*[itertools.combinations(range(n), ni) for ni in range(n + 1)]))

            # print(allsubsets(7))
            maxim = -1000000
            #print(potential_lines)
            if len(potential_lines)>20:
                continue
            subsets = allsubsets(len(potential_lines))
            #print("akr ",len(subsets))

            for i in range(len(subsets)):
                for j in subsets[i]:
                    abstraction_scores[i] = abstraction_scores[i] + potential_line_scores[j]
                if abstraction_scores[i] > maxim:
                    maxim = abstraction_scores[i]
                    optimal_abstraction_indices = subsets[i]
            #print("-------------g----------")

            optimal_abstraction_lines=[]
            inclusion_score=0
            exclusion_score=0
            inclusion_factor=0
            redundancy_factor=0
            if len(optimal_abstraction_indices):
                for i in optimal_abstraction_indices:
                    optimal_abstraction_lines.append(potential_lines[i])
            #print(potential_lines)
            #print("shikhar",optimal_abstraction_lines)
            actual_slice = eval(act_str)
            #print(actual_slice)
            #print(type(actual_slice))
            #print(type(actual_slice))
            # print(abstraction_scores)
            #print(optimal_abstraction_indices)
            actual_output = []
            if len(optimal_abstraction_lines)>0:
                for x in optimal_abstraction_lines:
                    if x in actual_slice:
                        inclusion_score = inclusion_score + 1
                    else:
                        exclusion_score = exclusion_score + 1
            size_of_slice = len(actual_slice)
            #print(size_of_slice)
            if len(actual_slice) > 0 and len(optimal_abstraction_lines) > 0:
                inclusion_factor = float(inclusion_score) / float(size_of_slice)
                redundancy_factor = float(exclusion_score) / float(len(optimal_abstraction_lines))
            #
            optimal_factors = (inclusion_factor, redundancy_factor)
            optimal_slice = optimal_abstraction_lines
            #print(actual_slice)
            #print("result",optimal_slice)
            #print(optimal_factors)
            #print(maxim)
            inclusion_factor_overall += inclusion_factor
            redundancy_factor_overall -= redundancy_factor
            optimal_factors_overall = (inclusion_factor_overall,redundancy_factor_overall)
            #print(wmax)
            #print("ankur",optimal_factors_overall)
        #print("-------------B----------")

    ###################################################### REPETITION ###################################################
    iterations = 2

    for i in range(iterations):
        w = []
        print("Processing")
        for i in range(0, 31):
            w.append(random.uniform(-1, 1))
        #print(w)
        wcurrent = w
        inclusion_factor_repeat = 0.0
        redundancy_factor_repeat = 0.0

        count_progs=0
        for filename in files:
            count_progs += 1
            if count_progs == 2:
                break
            c_fileName = "c_prog/"+filename
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

            v1 = MyCVisitor2()
            v1.visit(tree)
            #print("\n\n\n", v1.getCrudeCfg())
            #vari = input("Enter a variable name: ")
            #linenum = input("Enter a line number: ")


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
            line_features = [[0] * 8 for i in range(0,total_lines)]
            # print(line_features)


        ##################  ALL PREREQUISITE CALCULATIONS #####################################
            variables_list = v.getVarList()
            #print()
            c_outfile = "c_prog_slice_half/" + filename[:-2]+".txt"
            actual_slice_file = open(c_outfile, "r")

            #
            actual_slice_text = actual_slice_file.read().splitlines()
            #print("actual slice text - ",actual_slice_text)
            actual_slice_dictionary = {}
            for i in actual_slice_text:
                key_value = i.split(":")
                # print(key_value[0])
                # print(key_value[1])
                # key_value[1].replace(",\n",'')
                actual_slice_dictionary[key_value[0]] = key_value[1]
            new_slice = [i.replace('"', '') for i in actual_slice_dictionary]

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
                #print("ashishnew",temp_str1,temp_str2)
                vari = temp_str1
                linenum=temp_str2



                ################################### potential_lines ###########################
                index_linenum = cfg_list.index(linenum)
                potential_lines = list(range(1, int(linenum)))
                potential_flag = 0
                for i in range(index_linenum, -1, -1):
                    if cfg_list[i] == ']':
                        break
                    if cfg_list[i] == '[':
                        # print("yes")

                        if cfg_list[i - 2] == "while" or cfg_list[i-2]=="for":
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
                potential_line_features = feature_calculation(vari,linenum,cfg_textdict,cfg_list,total_lines,variables_list,potential_lines)

                for i in range(len(potential_line_scores)):
                    # line_scores.append(0)
                    for j in range(len(w)):
                        potential_line_scores[i] = potential_line_scores[i] + (w[j] * potential_line_features[i][j])
                #print(potential_lines)
                #print(potential_line_scores)
                if len(potential_lines) > 20:
                    continue

                abstraction_scores = [0] * (2 ** (len(potential_lines)))
                allsubsets = lambda n: list(itertools.chain(*[itertools.combinations(range(n), ni) for ni in range(n + 1)]))
                # print(allsubsets(7))
                maxim = -1000000
                if len(potential_lines) > 20:
                    continue

                subsets = allsubsets(len(potential_lines))
                #print(len(subsets))
                for i in range(len(subsets)):
                    for j in subsets[i]:
                        abstraction_scores[i] = abstraction_scores[i] + potential_line_scores[j]
                    if abstraction_scores[i] > maxim:
                        maxim = abstraction_scores[i]
                        optimal_abstraction_indices = subsets[i]
                optimal_abstraction_lines=[]
                inclusion_score=0
                exclusion_score=0
                inclusion_factor=0
                redundancy_factor=0
                if len(optimal_abstraction_indices):
                    for i in optimal_abstraction_indices:
                        optimal_abstraction_lines.append(potential_lines[i])
                #print(potential_lines)
                #print("shikhar",optimal_abstraction_lines)
                actual_slice = eval(act_str)
                #print(type(actual_slice))
                # print(abstraction_scores)
                #print(optimal_abstraction_indices)
                actual_output = []
                for x in optimal_abstraction_lines:
                    if x in actual_slice:
                        inclusion_score = inclusion_score + 1
                    else:
                        exclusion_score = exclusion_score + 1
                size_of_slice = len(actual_slice)
                #print(size_of_slice)
                if len(actual_slice) > 0 and len(optimal_abstraction_lines) > 0:
                    inclusion_factor = float(inclusion_score) / float(size_of_slice)
                    redundancy_factor = float(exclusion_score) / float(len(optimal_abstraction_lines))
                #
                optimal_factors = (inclusion_factor, redundancy_factor)
                optimal_slice = optimal_abstraction_lines
                #print(actual_slice)
                #print("result",optimal_slice)
                #print(optimal_factors)
                #print(maxim)

                inclusion_factor_repeat += inclusion_factor
                redundancy_factor_repeat -= redundancy_factor
        if inclusion_factor_repeat > inclusion_factor_overall and redundancy_factor_repeat < redundancy_factor_overall :
            wmax = wcurrent
            inclusion_factor_overall = inclusion_factor_repeat
            redundancy_factor_overall = redundancy_factor_repeat

        # if count_progs==1:
        #     break

    print(optimal_factors_overall)
    #print("Optimal w calculated is: ",wmax)


    with open('woptimal.txt', 'w') as f:
        for item in wmax:
            f.write("%s\n" % item)
        f.write(str(iterations))


    wfinalized = wmax

    ##################################  SLICE CHECKER : TESTING NEW SLICE ###########################################################

    w_two_thousand = [-0.9802029567666375, -0.5132642928713214, 0.5706250114071445, 0.025339485495515124, 0.8690276583782182, 0.655824155349916, 0.5022090912165711, 0.5051806922382631, 0.18557630733413233, 0.9212306986303516, 0.8968037088584999, 0.6437325270397469, 0.44476379829802837, -0.8536929468517367, 0.4222117335201401, -0.40847059242421513, 0.761763193101407, 0.35349177299679035, -0.21655973252123006, -0.9960377998232928, 0.7445876728783363, 0.5148185200640216, 0.7902944953631392, -0.5290561661682993, 0.9317691733109377, -0.7559530075150869, 0.9164650786054349, -0.8159237870065996, -0.6271712369874187, 0.02828103104751878, -0.4630512136868439]

    wmax = wfinalized
    print(wmax)

    while True:
        print("Enter 0 to stop testing , else enter 1")
        check = int(input())
        if check==0:
            break
        in_file = input("Enter the c program file name: ")
        #out_file = input("Enter the slice text file name: ")
        test_variable = input("Enter a variable name: ")
        test_line = input("Enter a line number: ")
        c_fileName = "c_prog/" + in_file
        c_outfile = "c_prog_slice_half/" + in_file[:-2] + ".txt"



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

        v1 = MyCVisitor2()
        v1.visit(tree)
        #print("\n\n\n", v1.getCrudeCfg())

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

        variables_list = v.getVarList()
        ################# potential lines #####################3
        index_linenum = cfg_list.index(test_line)
        #print(index_linenum)
        potential_lines = list(range(1, int(test_line)))
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
                            if (cfg_list[j] != test_line and int(cfg_list[j]) not in potential_lines):
                                potential_lines.append(int(cfg_list[j]))
                        j = j + 1
                    break
        #print(potential_lines)

        potential_line_features = []
        # for i in range(total_lines):
        #     if i + 1 in potential_lines:
        #         potential_line_features.append(line_features[i])
        # print(potential_line_features)
        potential_line_scores = [0] * len(potential_lines)

        potential_line_features = feature_calculation(test_variable, test_line, cfg_textdict, cfg_list, total_lines, variables_list,potential_lines)
        for i in range(len(potential_line_scores)):
            # line_scores.append(0)
            for j in range(len(wmax)):
                potential_line_scores[i] = potential_line_scores[i] + (wmax[j] * potential_line_features[i][j])
        #print(potential_line_scores)
        abstraction_scores = [0] * (2 ** (len(potential_lines)))
        allsubsets = lambda n: list(itertools.chain(*[itertools.combinations(range(n), ni) for ni in range(n + 1)]))
        maxim = -1000000
        subsets = allsubsets(len(potential_lines))
        #print(len(subsets))
        for i in range(len(subsets)):
            for j in subsets[i]:
                abstraction_scores[i] = abstraction_scores[i] + potential_line_scores[j]
            if abstraction_scores[i] > maxim:
                maxim = abstraction_scores[i]
                optimal_abstraction_indices = subsets[i]
        # print(abstraction_scores)
        #print(optimal_abstraction_indices)
        optimal_abstraction_lines = []
        if len(optimal_abstraction_indices):
            for i in optimal_abstraction_indices:
                optimal_abstraction_lines.append(potential_lines[i])
        #print(optimal_abstraction_lines)
        optimal_slice_final = optimal_abstraction_lines
        #print(optimal_slice_final)

        actual_slice_file = open(c_outfile, "r")
        actual_slice_text = actual_slice_file.read().splitlines()
        #print("actual slice text - ", actual_slice_text)
        actual_slice_dictionary = {}
        for i in actual_slice_text:
            key_value = i.split(":")
            # print(key_value[0])
            # print(key_value[1])
            # key_value[1].replace(",\n",'')
            actual_slice_dictionary[key_value[0]] = key_value[1]
        #new_slice = [i.replace('"', '') for i in actual_slice_dictionary]
        #print("new slice - ", new_slice)
        print("actual slice dictionary - ", actual_slice_dictionary)

        actual_slice_key = "('"+test_variable+"','"+test_line+"')"
        print("actual slice key - ",actual_slice_key)
        actual_slice = actual_slice_dictionary[actual_slice_key]
        print("updated actual slice - ", actual_slice)

        #
        ##########################   IGNORED  ######################################################
        # actual_slice_text = actual_slice_file.read().splitlines()
        # # print(actual_slice_text)
        # actual_slice_dictionary = {}
        # for i in actual_slice_text:
        #     key_value = i.split(":")
        #     # print(key_value[0])
        #     # print(key_value[1])
        #     # key_value[1].replace(",\n",'')
        #     actual_slice_dictionary[key_value[0]] = key_value[1]
        # act_str = actual_slice_dictionary[str((test_variable, test_line)).replace(' ', '')]
        # #print(act_str)
        actual_slice = eval(act_str)
        size_of_slice = len(actual_slice)
        inclusion_score=0.0
        exclusion_score=0.0
        inclusion_factor=0.0
        redundancy_factor=0.0
        # for x in optimal_abstraction_lines:
        #     if x in actual_slice:
        #         inclusion_score = inclusion_score + 1
        #     else:
        #         exclusion_score = exclusion_score + 1
        # size_of_slice = len(actual_slice)
        # # print(size_of_slice)
        # if len(actual_slice) > 0 and len(optimal_abstraction_lines) > 0:
        #     inclusion_factor = float(inclusion_score) / float(size_of_slice)
        #     redundancy_factor = float(exclusion_score) / float(len(optimal_abstraction_lines))
        # optimal_factors = (inclusion_factor,redundancy_factor)

        #########################################################################################
        print("Actual Slice is: ", actual_slice)
        print("Predicted Slice is: ", optimal_slice_final)
        #print("inclusion and redundancy factors are as follow: ",optimal_factors)
        #print(count_progs)
        #print(wfinalized)
        #w_twok = wfinalized
        #print(type(w_twok))
























if __name__ == '__main__':
    main()
