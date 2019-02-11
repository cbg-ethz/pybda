*****
PyBDA
*****

.. image:: http://www.repostatus.org/badges/latest/wip.svg
   :target: http://www.repostatus.org/#wip
.. image:: https://travis-ci.org/cbg-ethz/pybda.svg?branch=master
   :target: https://travis-ci.org/cbg-ethz/pybda/
.. image:: https://codecov.io/gh/cbg-ethz/pybda/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/cbg-ethz/pybda
.. image:: https://api.codacy.com/project/badge/Grade/1822ba83768d4d7389ba667a9c839638
   :target:
.. image:: https://www.codacy.com/app/simon-dirmeier/rnaiutilities_2?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=cbg-ethz/koios&amp;utm_campaign=Badge_Grade
   :target:
.. image:: https://readthedocs.org/projects/pybda/badge/?version=latest
   :target: http://pybda.readthedocs.io/en/latest

A commandline tool for analysis of big biological data sets using Snakemake, powered by Apache Spark.

.. image:: https://rawgit.com/dirmeier/dataframe/master/_fig/demo.svg
   :height: 600px

Introduction
============

PyBDA is a Python library and command line tool for big data analytics and machine learning scaling to tera byte sized data sets.

In order to make PyBDA scale to big data sets, we use `Apache Spark`_'s DataFrame API which, if developed against, automatically distributes
data to the nodes of a high-performance cluster and does the computation of expensive machine learning tasks in parallel.
For scheduling, PyBDA uses Snakemake_ to automatically execute pipelines of jobs. In particular, PyBDA will first build a DAG of methods/jobs
you want to execute in succession (e.g. dimensionality reduction into clustering) and then compute every method by traversing the DAG.
In the case of a successful computation of a job, PyBDA will write results and plots, and create statistics. If one of the jobs fails PyBDA will report where and which method failed
(owing to Snakemake's scheduling) such that the same pipeline can effortlessly be continued from where it failed the last time.

Documentation
=============

Check out the documentation `here <https://cbg-ethz.github.io/pybda/index.html>`_.
The documentation will walk you though

* the installation process,
* setting up Apache Spark,
* using `pybda`.

Author
======

Simon Dirmeier `simon.dirmeier at bsse.ethz.ch <mailto:simon.dirmeier@bsse.ethz.ch>`_.

.. _`Apache Spark`: https://spark.apache.org/
.. _Snakemake: https://snakemake.readthedocs.io/en/stable/