
db = ["breast-cancer-wisconsin.data","car.data","forestfires.csv","GlassData.csv",
     "qsar_fish_toxicity.csv","winequality-red.csv","iris.data","abalone.data","poker-hand-testing.data"]
for dbname in db:
    import time
    start_time = time.time()
    support = 2
    import os
    import psutil
    from collections import OrderedDict
    import operator
    print(support)
    if(dbname == "forestfires.csv"):
        delimiter = ","
    elif(".csv" in dbname):
        delimiter = ";"
    else:
        delimiter = ","
    #print(dbname,delimiter)
    
    def readData():
        cnt = 0
        fp = open(dbname,"r")   
        #fp = open("data.csv","r")
        dict_data = OrderedDict() # defaultdict(dict) 
        dict_count = {}
        for line in fp:
            if cnt == 0:
                val = line.strip('\n').split(delimiter)
                val1 = val
            if cnt >= 1:
                val = line.strip('\n').split(delimiter)
                dict_data[cnt-1] = [val[i] + chr(ord("a") + i) for i in range(0,len(val))]   #{val[i]: 1}
                for i in dict_data[cnt-1]:
                    if i not in dict_count.keys():
                        dict_count[i] = 1
                    else:
                        x = dict_count[i]
                        dict_count[i] = x + 1
            cnt += 1
        fp.close()
        tup_count = sorted(dict_count.items(), key=operator.itemgetter(1), reverse = True)
        dict_count = dict(tup_count)
        return dict_data,dict_count;
    #---------------------------------------------------------------------------------------------

    def create_header_table(data, d_count):
        header = d_count
        for k in header:
            header[k] = [header[k], None]
        return header
    #----------------------------------------------------------------------------------------------
    def sort_data(dataset,header):
        sort_dict = {}
        frequent_itemset = set(header.keys())
        for itemset,count in dataset.items():
            frequent_transaction = {}
            for item in count:
                if item in frequent_itemset:
                    frequent_transaction[item] = header[item][0]
                ordered_itemset = [v[0] for v in sorted(frequent_transaction.items(), key=lambda p: p[1], reverse=True)]
            sort_dict[itemset] = ordered_itemset
        return sort_dict

    #-----------------------------------------------------------------------------------------------------
    class Tree_Node:
        def __init__(self,Nodename,parentnode,count):
            self.name = Nodename
            self.count = count
            self.parent = parentnode
            self.children = {}
            self.nodelink = None

    #----------------------------------------------------------------------------------------------------------

    def create_tree(data,header,root):
        for val in data:
            if val in root.children:
                if root.name != 'root':
                    root.children[val].count = root.children[val].count + 1#root.count = 0
                else:
                    root.children[val].count = root.children[val].count + 1#root.count = root.count + 1
                root = root.children[val]
            else:
                root.children[val] = Tree_Node(val,root,1)
                root = root.children[val]
                if(header[val][1] == None):
                    header[val][1] = root
                else:
                    root_node = header[val][1]
                    while(root_node.nodelink != None):
                        root_node = root_node.nodelink
                    root_node.nodelink = root
    #--------------------------------------------------------------------------------------------------------------------

    def printTree(theRoot):
        if(len(theRoot.children)==0):
            return
        for child in theRoot.children:
            printTree(theRoot.children[child])
            #print("node is ", theRoot.children[child].name, "and count is ", theRoot.children[child].count)  
    #----------------------------------------------------------------------------------------------------------------

    def recur_getParentList(theNode):
        parentList=[]
        if(theNode.parent.name=="root"):
            parentList.append(theNode)
            return parentList
        parentList = parentList + recur_getParentList(theNode.parent)
        parentList.append(theNode)
        return parentList
    #-------------------------------------------------------------------------------------------------------
    def create_sub_header(parentLists, theNodeList):
        index=0
        header={}
        for someList in parentLists:
            for someNode in someList:
                if someNode.name != "root":
                    if someNode.name not in header.keys():
                        header[someNode.name]=theNodeList[index].count
                    else:
                        header[someNode.name]=header[someNode.name]+theNodeList[index].count
            index=index+1
        for k in header:
            header[k] = [header[k], None]
        return header   
    #-------------------------------------------------------------------------------------------------------------
    def create_subtree(header, theRoot, parentList, theCount):
        for someNode in parentList:
            if someNode.name in theRoot.children:
                theRoot.children[someNode.name].count = theRoot.children[someNode.name].count + theCount
            else:
                theRoot.children[someNode.name] = Tree_Node(someNode.name, theRoot, theCount)
                if(header[someNode.name][1] == None):
                    header[someNode.name][1] = theRoot.children[someNode.name]#someNode
                else:
                    root_node = header[someNode.name][1]
                    while(root_node.nodelink != None):
                        root_node = root_node.nodelink
                    root_node.nodelink = theRoot.children[someNode.name]
            theRoot = theRoot.children[someNode.name]
     #----------------------------------------------------------------------------------------------       
    def recur_moreThan1path(theRoot):#root can have many branches but if there is only 1 path in each branch, return false
        temp = False
        if len(theRoot.children)==0:
            return False
        for child in theRoot.children:
            if len(theRoot.children)>1:
                return True 
            else:
                temp = recur_moreThan1path(theRoot.children[child]) 
            if temp == True:
                return True
        return temp 
     #------------------------------------------------------------------------------------------------------

    def gen_base_fp(theRoot, theHeader):
        patternLists=[]
        for child in theRoot.children:
            patternLists = patternLists + all_subsets(theRoot.children[child], [])
        for item in theHeader:
            found = False
            for someList in patternLists:
                if len(someList) == 2:
                    if someList[-1]==item:
                        someList[0]=theHeader[item][0]
                        found = True
                        break
            if found == False:
                missingList = [theHeader[item][0], item]
                if missingList[0] >= support:                                      #pruning
                    patternLists.append(missingList)
        return patternLists
    #-----------------------------------------------------------------------------------------
    def copyList(theList):
        copy = []
        index=0
        while index < len(theList):
            copy.append(theList[index])
            index=index+1
        return copy
    #--------------------------------------------------------------------------------------------

    def all_subsets(theRoot, current_subsets):
        subsets = current_subsets
        next_set = []
        if theRoot.name!="root":
            if len(subsets)!=0:
                next_set=copyList(subsets[-1])
            else:
                next_set = [0]
            next_set.append(theRoot.name)
            next_set[0]=theRoot.count
            subsets.append(next_set)
        if(len(theRoot.children)==0):
            return subsets
        for child in theRoot.children:
            return all_subsets(theRoot.children[child], subsets)
    #-------------------------------------------------------------------------------------------------  

    def pruneTree(theRoot):
        if theRoot.name!='root':
            if theRoot.count < support:
                theRoot.parent.children.pop(theRoot.name)
                return
        if(len(theRoot.children)==0):
            return
        for child in list(theRoot.children):
            pruneTree(theRoot.children[child])
    #-------------------------------------------------------------------------------------------------      
    def generated_patterns_recur(theNode, skip1):
        #print("* ",theNode.name)
        theNodeList=[]
        theHeader={}
        while(theNode.nodelink!=None):
            theNodeList.append(theNode)
            theNode=theNode.nodelink
        theNodeList.append(theNode)
        #print("theNodeList is ", theNodeList)             #list of nodes from header slot complete
        parentLists=[]
        parentList=[]
        for node in theNodeList:
            if(node.parent.name!="root"):
                parentList=recur_getParentList(node.parent)
                parentLists.append(parentList)
        #print(parentLists)             #lists of parents for each node from header slot complete
        theHeader=create_sub_header(parentLists, theNodeList)
        #print(theHeader)               #new header from parent paths has been made (still missing links)
        newRoot = Tree_Node('root', None, theNode.count)
        index1=0
        for someList in parentLists:
            create_subtree(theHeader, newRoot, someList, theNodeList[index1].count)#theNode.count
            index1=index1+1
        pruneTree(newRoot)
        #printTree(newRoot)                             #subTree created
        multiplePaths = False
        for child in newRoot.children:
            multiplePaths = recur_moreThan1path(newRoot.children[child])
            if multiplePaths == True:
                break
        #print("multpaths is ", multiplePaths)         #determined if there are multiple paths
        fpList=[]
        if skip1 == False:
            for someNode in theNodeList:
                if someNode.parent.name == 'root':
                    if someNode.count >= support:      #prune
                        fpList.append([someNode.count])
        if multiplePaths == False:
            fpList = fpList + gen_base_fp(newRoot, theHeader)
        else:
            for elem in theHeader:
                fpList = fpList + generated_patterns_recur(theHeader[elem][1], False)
        for someList in fpList:
            someList.append(theNode.name)
        return fpList      
    #---------------------------------------------------------------------------------------------------------

    printCount=0
    data,d_count = readData()
    header_table = create_header_table(data, d_count)
    sort_dict = sort_data(data,header_table)
    root = Tree_Node('root',None,0)
    #print("----")
    for val in sort_dict.values():
        create_tree(val,header_table,root)
    #print("----")
    for item in header_table:
        thePatterns = generated_patterns_recur(header_table[item][1], True)
        #print("Patterns: ", thePatterns)
        printCount = printCount + len(thePatterns)
    print("Execution Time(Seconds)",time.time() - start_time)
    print(dbname,delimiter)
    print("# of patterns printed ", printCount)
    process = psutil.Process(os.getpid())
    print("Memory in MB",process.memory_info().rss/1000000) 
    print("--------------------")


