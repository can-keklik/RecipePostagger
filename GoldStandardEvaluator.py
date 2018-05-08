import string

import UtilsIO
import os
import pydot


def parseNode(node_str):
    ret_val = ""
    node_str = str(node_str).split('label="')
    if len(node_str) > 0:
        node_arr = str(node_str[1]).split('"];')
        ret_val = node_arr[int(len(node_arr) - 2)]
    return ret_val


def getRelationWithGoldGraph(graph):
    if len(graph) == 1:
        graph = graph[0]

    recipe = []
    for edge in graph.get_edge_list():
        destination = edge.get_destination()
        source = edge.get_source()
        destination_str = ""
        source_str = ""
        for node in graph.get_node_list():
            if str(destination) == node.get_name():
                destination_str = node.to_string()
            elif str(source) == node.get_name():
                source_str = node.to_string()
            if len(source_str) > 0 and len(destination_str) > 0:
                if (parseNode(source_str), parseNode(destination_str)) not in recipe:
                    recipe.append((parseNode(source_str), parseNode(destination_str)))
    return recipe


def getRelationWithPaperdGraph(graph):
    if len(graph) == 1:
        graph = graph[0]

    recipe = []
    for edge in graph.get_edge_list():
        destination = edge.get_destination()
        source = edge.get_source()

        if len(destination) > 0 and len(source) > 0:
            if (source, destination) not in recipe:
                recipe.append((source, destination))
    return recipe


def removepunc(word):
    return word.translate(None, string.punctuation)


def compareSourceAndDest(paper_src, paper_dest, gold_recipe):
    paper_src_list = str(paper_src).split(" ")
    paper_dest_list = str(paper_dest).split(" ")
    retVal = False
    gold_recipe = [(src, dest) for (src, dest) in gold_recipe if not "bon appetit" in dest]
    for src in paper_src_list:
        src = removepunc(src)
        for i, (gold_src, gold_dest) in enumerate(gold_recipe):
            gold_dest = str(gold_dest).split("\n")
            if len(gold_dest) > 0:
                gold_dest = gold_dest[0]
                gold_dest = removepunc(gold_dest)
            if src in gold_src:
                for dest in paper_dest_list:
                    dest = removepunc(dest)
                    if dest in gold_dest:
                        retVal = True
                        return retVal
            elif src in gold_dest:
                retVal =True


    return retVal


def compareTwoGraph(gold_recipe, paper_recipe):
    cnt = 0
    for i, (paper_source, paper_dest) in enumerate(paper_recipe):
        retVal = compareSourceAndDest(paper_source, paper_dest, gold_recipe)
        if retVal:
            cnt = cnt + 1
    if cnt > 0:
        return float(cnt)/float(len(paper_recipe))


current_path = os.getcwd()
gold_standart_folder_path = os.path.join(current_path, "results/AnnotationSession-goldgraph")
gold_standard_file_list = UtilsIO.getFileListWithFolderName(gold_standart_folder_path)
gold_standard_file_list = [file for file in gold_standard_file_list if ".svg" not in str(file)]

filename_list = UtilsIO.getFileNameList(gold_standart_folder_path)
filename_list = [file for file in filename_list if ".svg" not in str(file)]
filename_list = [str(file).split(".gv")[0] for file in filename_list]

paper_result_folder_path = os.path.join(current_path, "results/paper2")
paper_result_file_list = UtilsIO.getFileListWithFolderName(paper_result_folder_path)
paper_result_file_list = [file for file in paper_result_file_list if ".png" not in str(file)]
paper_result_filename_list = [str(file).split(".dot")[0] for file in filename_list]

graph = pydot.graph_from_dot_file(paper_result_file_list[0])
total = 0.0
cnt =0
for i, filename in enumerate(paper_result_filename_list):
    gold_standard_file = [file for file in gold_standard_file_list if filename in file]
    paper_result_file = [file for file in paper_result_file_list if filename in file]
    if len(gold_standard_file) > 0 and len(paper_result_file) > 0:
        try:
            gold_graph = pydot.graph_from_dot_file(gold_standard_file[0])
            paper_graph = pydot.graph_from_dot_file(paper_result_file[0])
            gold_standard_recipe = getRelationWithGoldGraph(gold_graph)
            paper_recipe = getRelationWithPaperdGraph(paper_graph)
            res = compareTwoGraph(gold_standard_recipe, paper_recipe)
            print(cnt,filename, res)
            total = total+res
            cnt = cnt+1

        except:
            print("file name error", filename)
            pass
print(len(paper_result_filename_list), cnt)
print("Result : ",float(total)/float(cnt))