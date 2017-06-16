#!/usr/bin/env python

import pandas
import numpy
from random import shuffle

import sklearn
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import sklearn.manifold

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx

import click

import os


def load_data():
    if os.path.isdir("/cluster/home/simondi/spark/"):
        filename = "/cluster/home/simondi/simondi/tix/data/screening_data/cells_sample_10_normalized.tsv"
    else:
        filename = "/Users/simondi/PHD/data/data/target_infect_x/screening_data_subset/cells_sample_10_normalized.tsv"

    data = pandas.read_csv(filename, sep="\t", header=0)

    feature_cols = [(i, x) for i, x in enumerate(data.columns.values) if
                    x.startswith("cells")]
    for i, c in feature_cols:
        data.loc[:, c] = data.loc[:, c].astype('float64')

    data_new = data.query(
      "library=='d' and design=='p' and replicate==1 and (pathogen=='brucella' or pathogen=='listeria' or pathogen=='adeno' or pathogen=='bartonella')").groupby(
      ["gene"]).filter(lambda x: len(x) == 40)

    del data_new["cells.children_invasomes_count"]
    del data_new["cells.children_bacteria_count"]

    X = data_new.dropna()

    return X


def get_models():
    pca = sklearn.decomposition.PCA(n_components=2)
    lle_h = sklearn.manifold.LocallyLinearEmbedding(10, n_components=2,
                                                    method='hessian')
    lle_m = sklearn.manifold.LocallyLinearEmbedding(10, n_components=2,
                                                    method='modified')
    lle_s = sklearn.manifold.LocallyLinearEmbedding(10, n_components=2,
                                                    method='standard')
    lle_l = sklearn.manifold.LocallyLinearEmbedding(10, n_components=2,
                                                    method='ltsa')
    mds = sklearn.manifold.MDS(n_init=1, max_iter=100, n_components=2)
    lda = LinearDiscriminantAnalysis(n_components=2)
    iso = sklearn.manifold.Isomap(30, n_components=2)
    spec = sklearn.manifold.SpectralEmbedding(n_components=2, random_state=0,
                                              eigen_solver="arpack")

    models = {
        "pca": pca,
        # "lle_hessian": lle_h,
        # "lle_modified": lle_m,
        "lle": lle_s,
        # "lle_ltsa": lle_l,
        "mds": mds,
        "lda": lda,
        "iso": iso,
        "spec": spec}

    return models


def plot(X, X_, fls, uni):
    uniq = list(set(X[uni]))

    hot = plt.get_cmap('hot')

    if uni == "gene":
        shuffle(uniq)
        uniq = uniq[1:10]

    cNorm = colors.Normalize(vmin=0, vmax=len(uniq))

    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=hot)
    plt.figure()
    alpha = 1 if uni == "gene" else 0.2
    for i in range(len(uniq)):
        indx = X[uni] == uniq[i]
        plt.scatter(X_[indx, 1], X_[indx, 0], color=scalarMap.to_rgba(i),
                    label=uniq[i], marker=".", alpha=alpha)

        plt.legend()

    if os.path.isdir("/cluster/home/simondi/spark/"):
        plt.savefig(
          "/cluster/home/simondi/PROJECTS/tix-util/tix_analysis/plots/scatter_" + fls + "_" + uni + ".png",
          dpi=720)
    else:
        plt.savefig(
          "/Users/simondi/PROJECTS/target_infect_x_project/src/tix_util/tix_analysis/plots/scatter_" + fls + "_" + uni + ".png",
          dpi=720)


@click.command()
@click.option('--model', help='The person to greet.', default="pca",
              type=click.Choice(["pca", "lle", "mds", "lda", "iso", "spec"]))
def run(model):
    print("Doing", model)
    mod = get_models()[model]

    X = load_data()
    feature_cols_idxs = [x for x in X.columns.values if
                         x.startswith("cells")]

    if mod is not None:
        X_ = mod.fit_transform(X.loc[:, feature_cols_idxs])
        plot(X, X_, model, "pathogen")
        plot(X, X_, model, "gene")
    else:
        print("Model was none")


if __name__ == '__main__':
    run()
