from CVisitor import CVisitor
from CParser import CParser





class MyHelper(CVisitor):

    def __init__(self, parser):
        self.parser = parser
        self.temp = set()
        self.functionDict = dict()
        self.defset={}
        self.useset={}

    def visitInitDeclarator(self, ctx:CParser.InitDeclaratorContext):
        return self.visitChildren(ctx)


    def getRuleName(self, ctx):
        if ctx == None:
            return ''
        if ctx.getChildCount() == 0:
            return ''
        s = str(ctx.toStringTree(recog=self.parser))
        #print(s)
        n = len(s)
        i = 0
        while not(s[i] == '('):
            i = i+1
        j = i+1
        while not(s[j] == ' '):
            j = j+1
        return s[i+1:j]

    def getVariableSet(self, ctx):
        res = self.generateRHS(ctx)
        res = res.union(self.generateLHS(ctx))
        #print(res)
        #input("wait")
        return res
    
    
    
    def isAssignEq(self, ctx):
        ruleName = self.getRuleName(ctx)
        # print(ruleName)

        assignEqSet = {"declaration", "expression"}
        if ruleName in assignEqSet:
            return True
        else:
            return False



    def generateRHS(self, ctx):
        res = []
        ruleName = self.getRuleName(ctx)
        if ruleName == "expression":
            if ctx.children[0].getChildCount()==3:
                res.append(ctx.children[0].children[2].getText())

        return res


    
    
    def generateLHS(self, ctx):
        if not(self.isAssignEq(ctx)):
            return []
        else:
            res = []
            temp_ctx = ctx
            ruleName = self.getRuleName(ctx)
            if ruleName=="declaration":
                if ctx.children[1].children[0].getChildCount()==3:
                    res.append(ctx.children[1].children[0].children[0].getText())



            if ruleName=="expression":
                if ctx.getChildCount()==1:
                    if ctx.children[0].getChildCount()==3:
                        res.append(ctx.children[0].children[0].getText())
                else:

                        res.append(ctx.children[2].children[0].getText())
                        res.append(ctx.children[0].children[0].children[0].getText())

            return res






























































































