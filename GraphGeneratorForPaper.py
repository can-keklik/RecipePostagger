import os

import pydot

subVerb_tag = "SUBVERB"
subIngre_Tag = "SUB_INGREIDENT"


class PaperGraphGenerator:
    graph = pydot.Dot(graph_type='digraph')

    # todo generate a graph like the papers'

    def __init__(self, taggedRecipe, relatedVerbs):
        self.taggedRecipe = taggedRecipe
        self.relatedVerbs = relatedVerbs

    def addHiddenEdge(self, node1, node2):
        self.graph.add_edge(
            pydot.Edge(node1, node2, label="Probable Ingredients", labelfontcolor="#009933", fontsize="10.0",
                       color="blue"))

    # return object     (word, tag, actionNode, indx, ingre_is)
    def createEdgesToSentence(self, sentence, indx):
        sentenceNodeArray = self.createSentenceNodes(sentence=sentence, indx=indx)
        actionNodeWhole = [(word, tag, node, indx) for (word, tag, node, indx) in sentenceNodeArray if tag == "VERB"]
        actionNodes = [node for (word, tag, node, indx) in sentenceNodeArray if tag == "VERB"]
        if len(actionNodes) == 0:
            return
        subActionNodes = [node for (word, tag, node, indx) in sentenceNodeArray if tag == subVerb_tag]
        subIngreNodes = [node for (word, tag, node, indx) in sentenceNodeArray if tag == subIngre_Tag]
        ingredientNodes = [node for (word, tag, node, indx) in sentenceNodeArray if tag == "INGREDIENT"]
        toolNodes = [node for (word, tag, node, indx) in sentenceNodeArray if tag == "TOOL"]
        actionNode = actionNodes[0]
        ingre_is = False
        if len(ingredientNodes) > 0:
            ingre_is = True
            for node in ingredientNodes:
                self.addEdge(node, actionNode)
        if len(toolNodes) > 0:
            for node in toolNodes:
                self.addEdge(node, actionNode)
        if len(subIngreNodes) > 0:
            if len(subActionNodes) > 0:
                for node in subIngreNodes:
                    self.addEdge(node, subActionNodes[0])
            else:
                for node in subIngreNodes:
                    self.addEdge(node, actionNode)
        if len(subActionNodes) > 0:
            for node in subActionNodes:
                self.addEdge(node, actionNode)

        (word, tag, node, indx) = actionNodeWhole[0]

        return (word, tag, actionNode, indx, ingre_is)

    # return array data type : (word, tag, node, indx)
    def createSentenceNodes(self, sentence, indx):
        tmp = [w for (w, t, ix) in sentence if t == "VERB"]
        tmp_idx_array = []
        sentenceNodes = []
        if len(tmp) > 0:
            for i in xrange(len(sentence)):
                (word, tag, index) = sentence[i]
                if tag == "VERB":
                    if word == tmp[0]:
                        nodeAction = self.createNode(tag, word)
                        sentenceNodes.append((word, tag, nodeAction, indx))
                    else:
                        node = self.createNode(subVerb_tag, word)
                        sentenceNodes.append((word, subVerb_tag, node, indx))
                        tmp_idx_array.append(i)
                elif tag == "INGREDIENT":
                    if self.checkIndex(i, tmp_idx_array):
                        node = self.createNode(tag, word)
                        sentenceNodes.append((word, subIngre_Tag, node, indx))
                    else:
                        node = self.createNode(tag, word)
                        sentenceNodes.append((word, tag, node, indx))

                elif tag == "TOOL":
                    node = self.createNode(tag, word)
                    sentenceNodes.append((word, tag, node, indx))

        return sentenceNodes

    def addEdge(self, node1, nodeAction):
        self.graph.add_edge(pydot.Edge(node1, nodeAction))

    def createGraph(self, dotFileName):
        tagRecipes = self.taggedRecipe
        sentenceActionNodes = []
        for i in xrange(len(tagRecipes)):
            sentenceActionNodes.append(self.createEdgesToSentence(sentence=tagRecipes[i], indx=i))
        for i in xrange(len(sentenceActionNodes)):
            self.addNodeToTheGraph(node_detailed=sentenceActionNodes[i], nodeArray=sentenceActionNodes)

        path = os.getcwd()
        if dotFileName:
            path = path + "/results/paper/"
            self.graph.write(path + dotFileName)

    def addNodeToTheGraph(self, node_detailed, nodeArray):
        (word, tag, actionNode, indx, ingre_is) = node_detailed
        last_node = self.getLastNode(nodeArray)
        fist_node = self.getFistIngreActionNode(nodeArray)
        if fist_node:
            if actionNode == fist_node:
                next_node = self.getNextNode(actionNode, nodeArray)
                if next_node:
                    self.addEdge(actionNode, next_node)
            elif actionNode == last_node:
                pass
            else:
                if ingre_is:
                    next_node = self.getNextNode(actionNode, nodeArray)
                    if next_node:
                        self.addEdge(actionNode, next_node)
                else:
                    node_forNonIngeAction = self.getNodeForNoneIngeNode(node_detailed, nodeArray)
                    if node_forNonIngeAction:
                        self.addEdge(actionNode, node_forNonIngeAction)
                    else:
                        next_node = self.getNextNode(actionNode, nodeArray)
                        if next_node:
                            self.addEdge(actionNode, next_node)

    def getNodeForNoneIngeNode(self, node, arr):
        (word, tag, action, indx, ingre_is) = node
        word_to_Link = self.get_word_to_link(node, arr)
        prevNode = self.getPrevNode(action, arr)
        for (word, tag, actionNode, indx, ingre_is) in arr:
            if word_to_Link == word:
                if actionNode != prevNode:
                    return actionNode
                else:
                    nextNode = self.getNextNode(action, arr)
                    if nextNode:
                        return nextNode

    def get_word_to_link(self, sentenceNode, arr):
        (word, tag, actionNode, indx, ingre_is) = sentenceNode
        w_to_link = ""
        w_p = 0
        next_node = self.getNexTuple(actionNode, arr)
        next_word = ""
        for (word_we_search, word_we_link_to, p) in self.relatedVerbs:
            if word == word_we_search:
                if len(w_to_link) == 0:
                    w_to_link = word_we_link_to
                    w_p = p
                    if next_node:
                        (w_f, t_f, n_f, idx_f, isIngre_f) = next_node
                        next_word = w_f
                        if str(w_to_link) in str(next_word):
                            w_to_link = next_word

                elif p > w_p:
                    if not str(w_to_link) in str(next_word):
                        w_to_link = word_we_link_to

        return w_to_link

    def createNode(self, TAG, word):
        if TAG == "VERB":
            node = self.createActionNode(word)
            self.graph.add_node(node)
            return node
        elif TAG == "TOOL":
            node = self.createToolNode(word)
            self.graph.add_node(node)
            return node
        elif TAG == "INGREDIENT":
            node = self.createIngredientNode(word)
            self.graph.add_node(node)
            return node
        elif TAG == "SUBVERB":
            node = self.createSubActionNode(word)
            self.graph.add_node(node)
            return node
        elif TAG == "PROBABLE":
            node = self.createProbableIngreNode(word)
            self.graph.add_node(node)
            return node
            # todo implement probable ingredients here

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

    def createSubActionNode(self, word):
        return pydot.Node(word, style="filled", fillcolor="#42e2f4")

    def checkIndex(self, i, i_arr):

        isTrue = False
        for ix in i_arr:
            if i > ix:
                isTrue = True

        return isTrue

    def getFistIngreActionNode(self, arr):
        if arr == None:
            return
        for i in xrange(len(arr)):
            (word, tag, actionNode, indx, ingre_is) = arr[i]
            if ingre_is:
                return actionNode

    def getNextNode(self, node, arr):
        for i, (w, t, n, idx, isIngre) in enumerate(arr):
            if i < len(arr) - 1:
                if node == n:
                    (w_f, t_f, n_f, idx_f, isIngre_f) = arr[i + 1]
                    return n_f

    def getNexTuple(self, node, arr):
        for i, (w, t, n, idx, isIngre) in enumerate(arr):
            if i < len(arr) - 1:
                if node == n:
                    return arr[i + 1]

    def getLastNode(self, arr):
        (w, t, n, idx, isIngre) = arr[len(arr) - 1]
        return n

    def getPrevNode(self, node, arr):
        for i, (w, t, n, idx, isIngre) in enumerate(arr):
            if i > 1:
                if node == n:
                    (w_f, t_f, n_f, idx_f, isIngre_f) = arr[i - 1]
                    return n_f
