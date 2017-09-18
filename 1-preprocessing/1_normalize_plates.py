#!/usr/bin/env python

import click


@click.command()
@click.argument("file", type=str)
def run(file):
    """
    Compute screen sets and their feature overlaps.
    """
    sets = _feature_sets(file)
    _max_set(sets)


if __name__ == '__main__':
    run()
