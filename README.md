# PyBDA <img src="https://raw.githubusercontent.com/cbg-ethz/pybda/master/_fig/sticker_pybda.png" align="right" width="160px"/>

[![Project Status](http://www.repostatus.org/badges/latest/wip.svg)](http://www.repostatus.org/#wip)
[![travis](https://img.shields.io/travis/cbg-ethz/pybda/master.svg?&logo=travis)](https://travis-ci.org/cbg-ethz/pybda/)
[![circleci](https://img.shields.io/circleci/project/github/cbg-ethz/pybda/master.svg?&logo=circleci)](https://circleci.com/gh/cbg-ethz/pybda/)
[![codecov](https://codecov.io/gh/cbg-ethz/pybda/branch/master/graph/badge.svg)](https://codecov.io/gh/cbg-ethz/pybda)
[![codedacy](https://api.codacy.com/project/badge/Grade/a4cca665933a4def9c2cfc88d7bbbeae)](https://www.codacy.com/app/simon-dirmeier/pybda?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=cbg-ethz/pybda&amp;utm_campaign=Badge_Grade)
[![readthedocs](https://readthedocs.org/projects/pybda/badge/?version=latest)](http://pybda.readthedocs.io/en/latest)
[![bioconda](https://img.shields.io/badge/install%20with-bioconda-brightgreen.svg?style=flat)](http://bioconda.github.io/recipes/pybda/README.html)
[![version](https://img.shields.io/pypi/v/pybda.svg?colorB=black&style=flat)](https://pypi.org/project/pybda/)

A commandline tool for analysis of big biological data sets using Snakemake and Apache Spark.

## About

PyBDA is a Python library and command line tool for big data analytics and machine learning scaling to tera byte sized data sets.

In order to make PyBDA scale to big data sets, we use [Apache Spark](https://spark.apache.org/)'s DataFrame API which, if developed against, automatically distributes
data to the nodes of a high-performance cluster and does the computation of expensive machine learning tasks in parallel.
For scheduling, PyBDA uses [Snakemake](https://snakemake.readthedocs.io/en/stable/) to automatically execute pipelines of jobs. In particular, PyBDA will first build a DAG of methods/jobs
you want to execute in succession (e.g. dimensionality reduction into clustering) and then compute every method by traversing the DAG.
In the case of a successful computation of a job, PyBDA will write results and plots, and create statistics. If one of the jobs fails PyBDA will report where and which method failed
(owing to Snakemake's scheduling) such that the same pipeline can effortlessly be continued from where it failed the last time.

For instance, if you want to first reduce your data set into a lower dimensional space and then cluster it using several cluster centers, you would first specify a config file similar to this:

```bash
$ cat config.yml

spark: spark-submit
infile: data/single_cell_imaging_data.tsv
outfolder: data
meta: data/meta_columns.tsv
features: data/feature_columns.tsv
dimension_reduction: factor_analysis
n_components: 5
clustering: kmeans
n_centers: 50, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200
sparkparams:
  - "--driver-memory=3G"
  - "--executor-memory=6G"
debug: true
```

Executing PyBDA, and calling the methods above, is then as easy as this:

```bash
$ pybda clustering config.yml local
```

## Installation

I recommend installing PyBDA from [Bioconda](https://bioconda.github.io/recipes/pybda/README.html?highlight=pybda#recipe-Recipe%20&#x27;pybda&#x27;):

```bash
$ conda install -c bioconda pybda
```

You can however also directly install using [PyPI](https://pypi.org/project/pybda/):

```bash
$ pip install pybda
```

Otherwise you could download the latest [release](https://github.com/cbg-ethz/pybda/releases) and install that.

## Documentation

Check out the documentation [here](https://pybda.readthedocs.io/en/latest/).
The documentation will walk you though

* the installation process,
* setting up Apache Spark,
* using `pybda`.

## Author

Simon Dirmeier <a href="mailto:simon.dirmeier@bsse.ethz.ch">simon.dirmeier@bsse.ethz.ch</a>
