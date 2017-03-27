import pydot


class GraphGenerator:
    graph = pydot.Dot(graph_type='digraph')
    listOfNodes = []

    def __init__(self, taggedRecipe, taggedIngreDient):
        self.taggedRecipe = taggedRecipe
        self.taggedIngredient = taggedIngreDient

    def createActionNode(self, word):
        return pydot.Node(word, style="filled", fillcolor="red")

    def createIngredientNode(self, word):
        return pydot.Node(word, style="filled", fillcolor="green")

    def createToolNode(self, word):
        return pydot.Node(word, style="filled", fillcolor="#0000ff")

    def createCommentNode(self, word):
        return pydot.Node(word, style="filled", fillcolor="#976856")

    def createProbableIngreNode(self, words):
        return pydot.Node(words, style="filled", fillcolor="#ffff66")

    def addHiddenEdge(self, node1, node2):
        self.graph.add_edge(
            pydot.Edge(node1, node2, label="Probable Ingredients", labelfontcolor="#009933", fontsize="10.0",
                       color="blue"))

    def createNode(self, TAG, word):
        if TAG == "VERB":
            return self.createActionNode(word)
        elif TAG == "TOOL":
            return self.createToolNode(word)
        elif TAG == "NAME":
            return self.createIngredientNode(word)
        elif TAG == "COMMENT":
            return self.createCommentNode(word)
            # todo implement probable ingredients here

    def createNODES(self):
        tagRecipes = self.taggedRecipe
        recipeNode = RecipeNode()
        for j in xrange(len(tagRecipes)):
            unions = self.unionWordAndTag(tagRecipes[j])
            print unions
            for i, (w, T) in enumerate(unions):
                node = self.createNode(T, w)
                if node:
                    if T == "VERB":
                        recipeNode.addActionNode(j, node)
                        self.graph.add_node(node)
                    elif T == "TOOL":
                        recipeNode.addToolNode(j, node)
                        self.graph.add_node(node)
                    elif T == "NAME":
                        recipeNode.addIngredientNode(j, node)
                        self.graph.add_node(node)
                    elif T == "COMMENT":
                        recipeNode.addCommentNode(j, node)
                        self.graph.add_node(node)

        return recipeNode

    def createGraph(self):
        recipeNode = self.createNODES()

        if len(recipeNode.actionNodeList) > 0:
            for j, (i, node) in enumerate(recipeNode.actionNodeList):
                if j < len(recipeNode.actionNodeList) - 1:
                    (index1, node1) = recipeNode.actionNodeList[j]
                    (index2, node2) = recipeNode.actionNodeList[j + 1]
                    self.graph.add_edge(pydot.Edge(node1, node2))
                    # action Nodes are added

            for j, (i, nodeAc) in enumerate(recipeNode.actionNodeList):
                for k, (l, nodeIngre) in enumerate(recipeNode.ingredientNodeList):
                    if i == l:
                        self.graph.add_edge(pydot.Edge(nodeIngre, nodeAc))
            for j, (i, nodeAc) in enumerate(recipeNode.actionNodeList):
                for k, (l, nodeTool) in enumerate(recipeNode.toolNodeList):
                    if i == l:
                        self.graph.add_edge(pydot.Edge(nodeTool, nodeAc))
        self.graph.write('es_graph.dot')

    def getNameEntityInIngre(self):
        returnArr = []
        for i in xrange(len(self.taggedRecipe)):
            arr = [wt for (wt, _) in self.taggedRecipe[i] if 'NAME' in _]
            if (len(arr) > 0):
                newW = " ".join(arr)
                returnArr.append(newW)
        return returnArr

    def getSpecificIngredient(self, word):
        ingList = self.getNameEntityInIngre()
        retIngre = ""
        for w in ingList:
            if word in w:
                retIngre = w

        return retIngre

    def unionWordAndTag(self, sentence):
        nameTagList = [wt for (wt, _) in sentence if ('NAME' == _)]
        allList = [wt for (wt, _) in sentence if ('NAME' == _ or 'QTY' == _ or "UNIT" == _)]
        unionList = []
        tmp = 1000
        if len(allList) > 0 and len(nameTagList) > 0:
            oldIndex = 0
            newSplitedList = []
            for i in xrange(len(nameTagList)):

                for j in xrange(len(allList)):
                    if nameTagList[i] == allList[j]:
                        a = allList[oldIndex:j + 1]
                        oldIndex = j + 1
                        newW = " ".join(a)
                        newSplitedList.append(newW)
            for i, (w, T) in enumerate(sentence):
                if T != "QTY" and T != "UNIT" and T != "NAME":
                    unionList.append((w, T))
                elif T == "NAME":
                    for j in xrange(len(newSplitedList)):
                        if w in newSplitedList[j]:
                            if tmp == 1000:
                                tmp = j
                                unionList.append((newSplitedList[j], "NAME"))
                            if (j == tmp):
                                break
                            else:
                                unionList.append((newSplitedList[j], "NAME"))
                                tmp = j

            return unionList
        else:
            return sentence




class RecipeNode:
    actionNodeList = []
    ingredientNodeList = []
    toolNodeList = []
    commentToolList = []

    def __init__(self):
        pass

    def addActionNode(self, i, node):
        self.actionNodeList.append((i, node))

    def addIngredientNode(self, i, node):
        self.ingredientNodeList.append((i, node))

    def addToolNode(self, i, node):
        self.toolNodeList.append((i, node))

    def addCommentNode(self, i, node):
        self.commentToolList.append((i, node))
