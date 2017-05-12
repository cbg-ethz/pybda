#!/usr/bin/env python

from __future__ import print_function
import random
import re


def sample(fl):
    m = {}
    with open(fl) as f:
        _ = f.readline()
        plates = f.readlines()
    random.shuffle(plates)
    for p in plates:
        line = p.split("\t")
        _, study, team, screen, plate = line[0].split('/')
        if line[1] != "ScreeningPlate" and study != 'TARGETINFECTX':
            continue
        try:
            li, sc = screen.split("-")[1:3]
            lv = list(sc)[0]
            if re.match(".*-[KG]\d+$", screen):
                pl = "_".join([study, team, li, lv])
                if pl not in m:
                    m[pl] = 1
                    print(line[0])
        except IndexError as e:
            1
        except ValueError as e:
            1
            # print("Whoops: ", line)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("USAGE:")
        print("\t$0 experiment_meta.tsv")
        exit()
    sample(sys.argv[1])
