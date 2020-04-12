import os

import pydot
import utils

class GraphGeneratorForPaper:

    PRED = "PRED"  # verb tag
    PRED_PREP = "PRED_PREP"  # verb tag with adp
    DOBJ = "DOBJ"  # obj that is not related with ingredient
    NON_INGREDIENT_SPAN = "NON_INGREDIENT_SPAN"  # obj that is not related with ingredient
    NON_INGREDIENT_SPAN_VERB = "NON_INGREDIENT_SPAN_VERB"  # obj that is not related with ingredient
    INGREDIENT_SPAN = "INGREDIENT_SPAN"  # obj that is related with ingredient
    INGREDIENTS = "INGREDIENTS"  # pure ingredient
    PARG = "PARG"  # tool
    PREP = "PREP"  # preposition
    PREDID = "PREDID"  # this id is realed with action's order

    def __init__(self, taggedRecipe, relatedVerbs):
        self.taggedRecipe = taggedRecipe
        self.relatedVerbs = relatedVerbs
        self.graph = pydot.Dot(graph_type='digraph')
        self.action_nodes = []
        self.par_edges_list = []

    def getEdges(self):
        return self.par_edges_list

    def addHiddenEdge(self, node1, node2):
        new_edge = pydot.Edge(node1, node2, label="Probable Ingredients", labelfontcolor="#009933", fontsize="10.0", color="blue")
        self.par_edges_list.append(new_edge)
        self.graph.add_edge(new_edge)

    def addEdge(self, node1, nodeAction):
        new_edge = pydot.Edge(node1, nodeAction)
        self.par_edges_list.append(new_edge)
        self.graph.add_edge(new_edge)

    def createGraph(self, dotFileName):
        for i in xrange(len(self.taggedRecipe)):
            snode = self.createSentenceNode(sentence=self.taggedRecipe[i])
            if snode != None:
                self.action_nodes.append(snode)
        if len(self.action_nodes) > 0:
            for node_detailed in self.action_nodes:
                self.addEdgeToActionNode(node_detailed=node_detailed)
        path = os.getcwd()
        if dotFileName:
            path = path + "/results/" + utils.FOLDER_NAME + "/"
            self.graph.write(path + dotFileName)

    def addEdgeToActionNode(self, node_detailed):
        (actionNode, action_word, ingre_is) = node_detailed
        last_node = self.getLastNode()
        fist_node = self.getFistIngreActionNode()

        if fist_node:
            if actionNode == fist_node:
                next_node = self.getNextNode(actionNode)
                if next_node:
                    self.addEdge(actionNode, next_node)
            elif actionNode == last_node:
                pass
            else:
                if ingre_is:
                    next_node = self.getNextNode(actionNode)
                    if next_node:
                        self.addEdge(actionNode, next_node)
                else:
                    node_forNonIngeAction = self.getNodeForNoneIngeNode(node_detailed)
                    if node_forNonIngeAction:
                        self.addEdge(actionNode, node_forNonIngeAction)
                    else:
                        next_node = self.getNextNode(actionNode)
                        if next_node:
                            self.addEdge(actionNode, next_node)

    def getNodeForNoneIngeNode(self, node):
        (action, word, ingre_is) = node
        word_to_Link = self.get_word_to_link(node)
        prevNode = self.getPrevNode(action)
        for (actionNode, word, ingre_is) in self.action_nodes:
            if str(word_to_Link) in str(word) and len(word_to_Link) > 0:
                if actionNode != prevNode:
                    return actionNode
                else:
                    nextNode = self.getNextNode(action)
                    if nextNode:
                        return nextNode

    def get_word_to_link(self, sentenceNode):
        (actionNode, word, ingre_is) = sentenceNode
        w_to_link = ""
        recipe = self.getRelationWithPaperdGraph()
        if len(recipe) > 0:
            tmp_dest = ""
            for (source, dest) in recipe:
                if word == source:
                    tmp_dest = dest
            recipe = [(s, d) for (s, d) in recipe if (s, d) != (word, tmp_dest)]
            for (s, d) in recipe:
                if d == tmp_dest:
                    w_to_link = s
        if len(w_to_link) == 0:
            w_p = 0
            word = str(word).split("-")[0]
            next_node = self.getNexTuple(actionNode)
            next_word = ""
            for (word_we_search, word_we_link_to, p) in self.relatedVerbs:
                if str(word) in str(word_we_search):
                    if len(w_to_link) == 0:
                        w_to_link = word_we_link_to
                        w_p = p
                        if next_node:
                            (n_f, w_f, isIngre_f) = next_node
                            next_word = w_f
                            if str(w_to_link) in str(next_word):
                                w_to_link = next_word

                    elif p > w_p:
                        if not str(w_to_link) in str(next_word):
                            w_to_link = word_we_link_to
                    elif p < w_p:
                        if str(word) in str(next_word):
                            w_to_link = next_word
                elif str(word) in str(word_we_link_to):
                    if len(w_to_link) == 0:
                        w_to_link = word_we_search
                        w_p = p
                        if next_node:
                            (n_f, w_f, isIngre_f) = next_node
                            next_word = w_f
                            if str(w_to_link) in str(next_word):
                                w_to_link = next_word

                    elif p > w_p:
                        if not str(w_to_link) in str(next_word):
                            w_to_link = word_we_link_to
                    elif p < w_p:
                        if str(word) in str(next_word):
                            w_to_link = next_word
            tmp = [(word_we_search, word_we_link_to, p) for (word_we_search, word_we_link_to, p) in
                   self.relatedVerbs if
                   word_we_search != w_to_link and word_we_link_to != w_to_link and word_we_search != word and word_we_link_to != word]
            self.relatedVerbs = []
            self.relatedVerbs = tmp
        return w_to_link

    def createSentenceNode(self, sentence):
        pred_prep = [(word, tag, idx) for (word, tag, idx) in sentence if tag == self.PRED_PREP]
        action_node = ()
        word_return = ""
        is_Ingre = False
        ingres = [(word, tag, idx) for (word, tag, idx) in sentence if tag == self.INGREDIENTS]
        if len(ingres) > 0:
            is_Ingre = True
        if len(pred_prep) > 0:
            (word, tag, idx) = pred_prep[0]
            if len(word) > 0:
                action_node = self.createNode(word=word, TAG=tag, idx=idx)
                word_return = word
        else:
            try:
                pred = [(word, tag, idx) for (word, tag, idx) in sentence if tag == self.PRED]
                (word, tag, idx) = pred[0]
                if len(word) > 0:
                    action_node = self.createNode(word=word, TAG=tag, idx=idx)
                    word_return = word
            except:
                print(sentence)
                print("createSentenceNode warning")
                return None

        others = [(word, tag, idx) for (word, tag, idx) in sentence if tag != self.PRED_PREP and tag != self.PRED]
        if len(others) > 0:
            for (word, tag, idx) in others:
                if len(word) > 0:
                    node = self.createNode(word=word, TAG=tag, idx=idx)
                    if node and self.checkDoubleLink(word_return, word):
                        self.addEdge(node1=node, nodeAction=action_node)
        return (action_node, word_return + "-" + str(idx), is_Ingre)

    def createNode(self, TAG, word, idx):
        if TAG == self.PRED or TAG == self.PRED_PREP:
            node = self.createActionNode(str(word) + " " + str(idx))
            self.graph.add_node(node)
            return node
        elif TAG == self.PARG:
            node = self.createToolNode(str(word))
            self.graph.add_node(node)
            return node
        elif TAG == self.INGREDIENTS:
            node = self.createIngredientNode(str(word))
            self.graph.add_node(node)
            return node
        elif TAG == self.NON_INGREDIENT_SPAN_VERB:
            node = self.createSubActionNode(str(word))
            self.graph.add_node(node)
            return node
        elif TAG == self.NON_INGREDIENT_SPAN:
            node = self.createProbableIngreNode(str(word))
            self.graph.add_node(node)
            return node
        elif TAG == self.DOBJ:
            node = self.createDOBJNode(str(word))
            self.graph.add_node(node)
            return node
        elif TAG == self.INGREDIENT_SPAN:
            node = self.createINGRESPANNode(str(word))
            self.graph.add_node(node)
            return node
            # todo implement probable ingredients here

    def getRelationWithPaperdGraph(self):

        graph = self.graph

        recipe = []
        for edge in self.getEdges(): #graph.get_edge_list():
            destination = edge.get_destination()
            source = edge.get_source()

            if len(destination) > 0 and len(source) > 0:
                if (source, destination) not in recipe:
                    recipe.append((source, destination))
        return recipe

    def checkDoubleLink(self, action_word, other_word):

        graph = self.graph

        retVal = True
        for edge in self.getEdges(): #graph.get_edge_list():
            destination = edge.get_destination()
            source = edge.get_source()
            if str(action_word) in str(destination) and str(other_word) in str(source):
                retVal = False
        return retVal

    def createActionNode(self, word):
        # return pydot.Node(word, style="filled", fillcolor="red")
        return pydot.Node(word, style="filled", shape="circle", fillcolor="white")

    def createIngredientNode(self, word):
        # return pydot.Node(word, style="filled", fillcolor="green")
        return pydot.Node(word, style="filled", shape="hexagon", fillcolor="white")

    def createToolNode(self, word):
        # return pydot.Node(word, style="filled", fillcolor="#0000ff")
        return pydot.Node(word, style="filled", shape="box", fillcolor="white")

    def createCommentNode(self, word):
        # return pydot.Node(word, style="filled", fillcolor="#976856")
        return pydot.Node(word, style="filled", shape="trapezium", fillcolor="white")

    def createProbableIngreNode(self, words):
        # return pydot.Node(words, style="filled", fillcolor="#ffff66")
        return pydot.Node(words, style="filled", shape="rectangle", fillcolor="white")

    def createSubActionNode(self, word):
        # return pydot.Node(word, style="filled", fillcolor="#42e2f4")
        return pydot.Node(word, style="filled", shape="ellipse", fillcolor="white")

    def createDOBJNode(self, word):
        # return pydot.Node(word, style="filled", fillcolor="#FFBF00")
        return pydot.Node(word, style="filled", shape="parallelogram", fillcolor="white")

    def createINGRESPANNode(self, word):
        # return pydot.Node(word, style="filled", fillcolor="#01DFA5")
        return pydot.Node(word, style="filled", shape="hexagon", fillcolor="white")

    def getFistIngreActionNode(self):
        for i in xrange(len(self.action_nodes)):
            arr = self.action_nodes
            (action_node, word_return, is_Ingre) = arr[i]
            if is_Ingre:
                return action_node

    def getNextNode(self, node):
        for i, (action_node, word_return, is_Ingre) in enumerate(self.action_nodes):
            if i < len(self.action_nodes) - 1:
                if node == action_node:
                    (n_f, w_f, isIngre_f) = self.action_nodes[i + 1]
                    return n_f

    def getNexTuple(self, node):
        for i, (n, w, isIngre) in enumerate(self.action_nodes):
            if i < len(self.action_nodes) - 1:
                if node == n:
                    return self.action_nodes[i + 1]

    def getLastNode(self):
        (action_node, word_return, is_Ingre) = self.action_nodes[len(self.action_nodes) - 1]
        return action_node

    def getPrevNode(self, node):
        for i, (action_node, word_return, is_Ingre) in enumerate(self.action_nodes):
            if i > 1:
                if node == action_node:
                    (n_f, wrd_f, isIngre_f) = self.action_nodes[i - 1]
                    return n_f
