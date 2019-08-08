*****
PyBDA
*****

A commandline tool for analysis of big biological data sets for distributed HPC clusters.

About
=====

PyBDA is a Python library and command line tool for big data analytics and machine learning scaling to tera byte sized data sets.

In order to make PyBDA scale to big data sets, we use `Apache Spark`_'s DataFrame API which, if developed against, automatically distributes
data to the nodes of a high-performance cluster and does the computation of expensive machine learning tasks in parallel.
For scheduling, PyBDA uses Snakemake_ to automatically execute pipelines of jobs. In particular, PyBDA will first build a DAG of methods/jobs
you want to execute in succession (e.g. dimensionality reduction into clustering) and then compute every method by traversing the DAG.
In the case of a successful computation of a job, PyBDA will write results and plots, and create statistics. If one of the jobs fails PyBDA will report where and which method failed
(owing to Snakemake's scheduling) such that the same pipeline can effortlessly be continued from where it failed the last time.

Documentation
=============

Check out the documentation `here <https://pybda.readthedocs.io/en/latest/>`_.
The documentation will walk you though

* the installation process,
* setting up Apache Spark,
* using `pybda`.

Author
======

Simon Dirmeier `simon.dirmeier at bsse.ethz.ch <mailto:simon.dirmeier@bsse.ethz.ch>`_.

.. _`Apache Spark`: https://spark.apache.org/
.. _Snakemake: https://snakemake.readthedocs.io/en/stable/