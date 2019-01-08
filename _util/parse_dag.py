#!/usr/bin/env python

import click
import re

node_match = re.compile("^\s+\d+\[.*$")
edge_match = re.compile("^\s+(\d+)\s->\s(\d+)\s+$")
label_match = re.compile("^\s+(\d+)\[label\s\=\s\"(.*?)\".*$")


def process_line(line, base_nodes):
    if "graph[" in line:
        print("\tgraph[bgcolor=white, margin=0,fontname=\"Roboto\"];")
    elif "node[" in line:
        print("\tnode[shape=rectangle, "
              "fontname=\"Roboto\", fontsize=10, penwidth=2];")
    elif "edge[" in line:
        print("\tedge[penwidth=1, color=grey80, arrowsize=.8];")
        print("\tnodesep=1.5;")
    elif node_match.match(line):
        match = label_match.match(line)
        idx, label = match.group(1), match.group(2)
        base_nodes[label] = int(idx)
        if int(idx) != 0:
            print("\t" + idx + "[label = \"" + label +
                  "\", shape=\"rectangle\"]")
    elif edge_match.match(line):
        match = edge_match.match(line)
        fr, to = match.group(1), match.group(2)
        if int(fr) == 1 and int(to) == 0:
            all_node = str(1 + max(base_nodes.values()))
            print("\t" + all_node + "[label = \"data\", shape=\"rectangle\"];")
            for k in ["fa", "pca", "kpca"]:
                print("\t" + all_node + " -> " + str(base_nodes[k]))
        if int(to) != 0:
            print("\t" + fr + " -> " + to)
    else:
        print(line.strip())


@click.command()
@click.argument("file", type=click.File('r'))
def run(file):
    base_nodes = {}
    for line in file:
        process_line(line, base_nodes)


if __name__ == "__main__":
    run()
