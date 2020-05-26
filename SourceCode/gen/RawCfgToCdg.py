class RawCfgToCdg():

    def __init__(self, rawCfg, cfg):  # here 'tree'=RawCfg
        self.tree = rawCfg
        self.dot_str = ""
        self.cfg = cfg
        self.pdict =  {}

    def execute(self):
        tokens = self.modifyRawCfg()
        f, l = self.cfgReader(tokens, 0, len(tokens) - 1)
        self.dot_str = "\n\tstart -> " + f + ";" + self.dot_str
        for i in l:
            self.dot_str = self.dot_str + "\n\t" + i + " -> exit;"
        self.dot_str = "# dot file created at runtime\n" + "\ndigraph G {" + self.dot_str
        self.dot_str = self.dot_str + "\n\n\tstart [shape=Msquare, color=green];\n\texit [shape=Msquare, color=red];\n}"
        # print("\n\n", self.dot_str)
        self.cfg.dotGraph = self.dot_str

    def modifyRawCfg(self):
        self.tree = self.tree.replace("  ", " ")
        self.tree = self.tree.strip()
        tokens = self.tree.split(" ")
        return tokens


    def tree_util(self,data,parent): # todo: need to  add else condtion and switch statements
        while_check = 0
        while_parent = 0
        last=""
        for i in data:
            if type(i)==str and i.isdigit():
                self.pdict[int(i)]=parent
                last=i
            elif type(i)==str and i.find('if')!=-1:
                last=i.replace('if_','')
                self.pdict[int(last)]=parent
            elif type(i)==str and i.find('while')!=-1:
                while_check = 1
                last=i.replace('while_','')
                self.pdict[int(last)]=parent
                while_parent=last
            elif type(i) == str and i.find('for') != -1:
                while_check = 1
                last = (i.replace('for_', ''))
                self.pdict[int(last)] = parent
                while_parent = last
            elif type(i)==list:
                if type(i[0])==str:
                    if i[0].find("if")!=-1:
                        x = self.tree_util(i,parent)
                    elif i[0].find("while")!=-1:
                        x = self.tree_util(i,parent)
                        parent=i[0].replace('while_','')
                    elif i[0].find("for")!=-1:
                        x = self.tree_util(i,parent)
                        parent=i[0].replace('for_','')
                    else:
                        x = self.tree_util(i, last)
                else:
                    x = self.tree_util(i,last)


    def push(self, obj, l, depth):
        while depth:
            l = l[-1]
            depth -= 1

        l.append(obj)

    def parse(self,s):
        groups = []
        depth = 0

        try:
            # print(s.split())
            for char in s.split(" "):
                # print("-"+char+"-")
                if char=='':
                    continue
                if char == '[':
                    self.push([], groups, depth)
                    depth += 1
                elif char == ']':
                    depth -= 1
                else:
                    self.push(char, groups, depth)
        except IndexError:
            raise Exception('Parentheses mismatch')

        if depth > 0:
            raise Exception('Parentheses mismatch')
        else:
            return groups



    def tree_make(self):
        data = self.parse(self.tree.replace("\n",""))
        #print("Data in tree_make in RawCfgToCdg - ",data)
       #print("data.length = ", len(data))
        self.tree_util(data,None)
        return  self.pdict
        # print("Parents CDG ---->>>>  ",self.pdict)