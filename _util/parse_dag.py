#!/usr/bin/env python

import click
import re

node_match = re.compile("^\s+\d+\[.*$")
edge_match = re.compile("^\s+(\d+)\s->\s(\d+)\s+$")
label_match = re.compile("^\s+(\d+)\[label\s\=\s\"(.*?)\".*$")


def process_line(line, nodes, edges):
    if node_match.match(line):
        match = label_match.match(line)
        idx, label = match.group(1), match.group(2)
        nodes[idx] = label
    elif edge_match.match(line):
        match = edge_match.match(line)
        fr, to = match.group(1), match.group(2)
        edges.append([fr, to])


@click.command()
@click.argument("file", type=click.File('r'))
def run(file):
    nodes = {}
    edges = []
    for line in file:
        process_line(line, nodes, edges)
    for [fr, to] in edges:
        print(nodes[fr], "\t", nodes[to])


if __name__ == "__main__":
    run()
