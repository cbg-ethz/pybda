PyBDA
=====

.. image:: http://www.repostatus.org/badges/latest/wip.svg
   :target: http://www.repostatus.org/#wip
   :alt: Status
.. image:: https://travis-ci.org/cbg-ethz/pybda.svg?branch=master
   :target: https://travis-ci.org/cbg-ethz/pybda/
   :alt: Travis
.. image:: https://codecov.io/gh/cbg-ethz/pybda/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/cbg-ethz/pybda
   :alt: Codecov
.. image:: https://api.codacy.com/project/badge/Grade/a4cca665933a4def9c2cfc88d7bbbeae
   :target: https://www.codacy.com/app/simon-dirmeier/pybda?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=cbg-ethz/pybda&amp;utm_campaign=Badge_Grade
   :alt: Codacy
.. image:: https://readthedocs.org/projects/pybda/badge/?version=latest
   :target: https://pybda.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation

A commandline tool for analysis of big biological data sets using Snakemake, powered by Apache Spark.

.. toctree::
   :hidden:
   :maxdepth: 2
   :titlesonly:

   Home <self>
   usage
   usecase_dimred
   usecase_clustering
   usecase_regression

About
-----

Welcome to PyBDA.

PyBDA is a Python library and command line tool for big data analytics and machine learning scaling to tera byte sized data sets.

In order to make PyBDA scale to big data sets, we use Apache [Spark]_'s DataFrame API which, if developed against, automatically distributes
data to the nodes of a high-performance cluster and does the computation of expensive machine learning tasks in parallel.
For scheduling, PyBDA uses [Snakemake]_ to automatically execute pipelines of jobs. In particular, PyBDA will first build a DAG of methods/jobs
you want to execute in succession (e.g. dimensionality reduction into clustering) and then compute every method by traversing the DAG.
In the case of a successful computation of a job, PyBDA will write results and plots, and create statistics. If one of the jobs fails PyBDA will report where and which method failed
(owing to Snakemake's scheduling) such that the same pipeline can effortlessly be continued from where it failed the last time.

Sofar PyBDA supports several methods from [MLLib]_ and some that have been developed from scratch to scale to big data settings:

* dimensionality reduction using PCA, factor analysis, kPCA, linear discriminant analysis and ICA,
* clustering using k-means and Gaussian mixture models,
* supervised learning using generalized linear regression models, random forests and gradient boosting.

The package is actively developed and will add new features in a timely fashion. If you want to you can also contribute:
`fork us on GitHub <https://github.com/cbg-ethz/biospark>`_.

Dependencies
------------

* Apache Spark >= 2.3.0
* Python >= 3.6

Example
-------

PyBDA only requires a config-file and, if possible, the IP of a spark-cluster. Otherwise you can just call PyBDA locally using ``local``).
The config file might for a simple clustering case look like this:

.. literalinclude:: ../../pybda-usecase-clustering.config
  :caption: Contents of ``pybda-usecase-clustering.config`` file
  :name: pybda-usecase-gmm.config

This would fight several k-means clusterings with different numbers of clusters.
Calling the tool is then as simple as:

.. code-block:: bash

   pybda clustering pybda-usecase-kmeans.config local

The result of any call creates several different data files and appropriate distributions.
For instance, for the example above, two of the plots generated are shown below:

.. figure:: _static/kmeans-profile.png
   :align: center

   Number of clusters vs explained variance and BIC.

.. figure:: _static/kmeans-cluster_sizes-histogram.png
   :align: center

   Each row shows the distribution of the number of cells per cluster (component).


References
----------

.. [Snakemake] `Köster, Johannes, and Sven Rahmann. "Snakemake—a scalable bioinformatics workflow engine." Bioinformatics 28.19 (2012): 2520-2522. <https://doi.org/10.1093/bioinformatics/bts480>`_
.. [Spark]     `Zaharia, Matei, et al. "Apache spark: a unified engine for big data processing." Communications of the ACM 59.11 (2016): 56-65. <https://doi.org/10.1145/2934664>`_
.. [MLLib]     `Meng, Xiangrui, et al. "Mllib: Machine learning in apache spark." The Journal of Machine Learning Research 17.1 (2016): 1235-1241. <http://jmlr.org/papers/volume17/15-237/15-237.pdf>`_
