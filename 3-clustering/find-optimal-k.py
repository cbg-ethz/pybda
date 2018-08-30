import argparse
import sys
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans


cluster_sequence = list(range(2, 10, 2)) + \
                   [20, 30, 40, 50, 75, 100, 200, 300, 500]


def bic(rss, N, K, P):
    return N + N * np.log(2 * np.pi) + \
           N * np.log(rss / N) + \
           np.log(N) * (K + P + 1)


def read_args(args):
    parser = argparse.ArgumentParser(
      description='Find the optimal K for a data set.')
    parser.add_argument('-f',
                        type=str,
                        help='tsv file that has feature columns, '
                             'e.g. outlier-removal-1000.tsv',
                        required=True,
                        metavar="input-folder")
    parser.add_argument('-o',
                        type=str,
                        help='output file suffix, i.e. really a suffix',
                        required=True,
                        metavar="output file")
    opts = parser.parse_args(args)

    return opts.f, opts.o, opts


def _plt(df, n_obs, outfile):
    min_idx = np.argmin(df["BIC"].values)

    plt.style.use(["seaborn-whitegrid"])
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Verdana']

    _, ax = plt.subplots(figsize=(7, 4), dpi=720)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.set_label_coords(x=.9, y=-0.1)
    ax.yaxis.set_label_coords(x=-0.10, y=.95)
    ax.grid(linestyle="")
    ax.grid(which="major", axis="x", linestyle="-", color="gainsboro")
    ax.spines['bottom'].set_color('black')
    ax.spines['left'].set_color('black')

    ax.plot(df["K"], df["BIC"], "black", alpha=.5, marker="o")
    ax.plot(df["K"].iloc[min_idx], df["BIC"].iloc[min_idx], "red",
            alpha=.5,marker="o")
    plt.text(df["K"].iloc[min_idx], df["BIC"].iloc[min_idx],
             int(df["K"].iloc[min_idx]))

    plt.xlabel('Number of clusters', fontsize=15)
    plt.ylabel("BIC", fontsize=15)
    plt.title("BIC for clusterings for data of size n = " + str(n_obs))
    plt.savefig(outfile + ".png")


def run():
    # check files
    infile, outfile, opts = read_args(sys.argv[1:])
    table = pd.read_csv(infile, sep="\t")
    features = table.iloc[:, 10:].values

    n, p = features.shape
    n_obs = 10 ** np.ceil(np.log10(n))

    df = pd.DataFrame({'K': [], 'SSE': [], 'BIC': []})
    Ks = list(map(lambda x: int(x * (n_obs / 1000)), cluster_sequence))
    print(Ks)
    for k in Ks:
        if k < 1:
            continue
        print(k)
        km = KMeans(n_clusters=k)
        mod = km.fit(features)
        sse = mod.inertia_
        bic_ = bic(sse, features.shape[0], k, features.shape[1])
        df2 = pd.DataFrame({'K': [k], 'SSE': [sse], 'BIC': [bic_]})
        df = df.append(df2)

    df.to_csv(outfile + ".csv", index=False)
    _plt(df, n_obs, outfile)


if __name__ == "__main__":
    run()
