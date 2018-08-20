Κοῖος /ˈci.os/ 
==============

.. image:: http://www.repostatus.org/badges/latest/active.svg
   :target: http://www.repostatus.org/#active
.. image:: https://travis-ci.org/cbg-ethz/koios.svg?branch=master
   :target: https://travis-ci.org/cbg-ethz/koios/
.. image:: https://codecov.io/gh/cbg-ethz/koios/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/cbg-ethz/koios/
.. image:: https://api.codacy.com/project/badge/Grade/1822ba83768d4d7389ba667a9c839638
   :target: https://www.codacy.com/app/simon-dirmeier/rnaiutilities_2?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=cbg-ethz/rnaiutilities&amp;utm_campaign=Badge_Grade
.. image:: https://readthedocs.org/projects/koios/badge/?version=latest
   :target: http://koios.readthedocs.io/en/latest/
   :alt: doc


A workflow manager for analysis of big biological data sets using Snakemake, powered by Apache Spark.


.. toctree::
   :hidden:
   :maxdepth: 4

   Home <self>
   usecase
   pipeline

.. raw:: html

    <div align="center" style="text-align: middle">
    <object data="_static/snakeflow.svg" type="image/svg+xml" width="700"></object>
    The <i>koios</i> workflow.
    </div>

Introduction
------------

Welcome to ``koios``.

``koios`` is a Python/Scala library for analysis of big biological data sets.
We use Apache Spark as analytics engine for big data processing and machine learning,
and Snakemake for scheduling.

With ``koios``

* Preprocessing: dimension reduction and outlier removal
* Clustering
* Visualizations

The library is still under development, so if you'd like to contribute,
`fork us on GitHub <https://github.com/cbg-ethz/biospark>`_.

Dependencies
------------

* Apache Spark >= 2.3.0
* JDK >= 1.7
* openmpi
* Scala >= 2.12.0
* R >= 3.5.0
* Python >= 3.6
* sparkhpc

Installation
------------

1) Make sure to have ``python3`` installed. ``koios`` does not support
previous versions. The best way to do that is to download `anaconda <https://www.continuum.io/downloads>`_ and create a
virtual `environment <https://conda.io/docs/using/envs.html>`_.

2) Download the latest `release <https://github.com/cbg-ethz/biospark/releases>`_ first and unpack it.

3) Install the required dependencies using:

.. code-block:: bash

  ./install_dependencies.sh

4) Install `Apache Spark <https://spark.apache.org/downloads.html>`_ . Use the *prebuilt for Apache Hadoop* package type.

5) That is it.

Usage
-----

Using ``koios`` requires providing a config file and starting a spark cluster.
We assume that you are familiar with using a spark standalone cluster, so we only briefly
discuss how the cluster is started.

Config
~~~~~~~

Your configuration file will need to have the following format:

.. literalinclude:: ../../biospark-local.config
  :caption: Contents of ``biospark-local.config`` file
  :name: biospark-local.config


The first line points to the ``spark-submit`` command which is provided by Apache Spark.
The second line contains the ``tsv`` with your data, while the third line is the *folder* where all outputs are saved to.
We use factor analysis for dimension reduction for which number of latent features is determined by ``factors``.
The output of the dimension reduction will be used for clustering.
We apply a recursive clustering method that finds the optimal number of cluster
centers *K*. For this, you need to provide the maximal number of cluster centers,
since we use this as a reference point.
Finally ``sparkparams`` contains the parameters you want to provide spark with.
The Spark `documentation <https://spark.apache.org/docs/latest/submitting-applications.html>`_
for submitting applications provides details which arguments are valid here.

Spark
~~~~~~

In order for `biospark` to work you need to have a working
*standalone spark environment* set up, running and listening to some ``IP``.
You can find a good introduction
`here <https://spark.apache.org/docs/latest/spark-standalone.html>`_ on how
to start the standalone Spark cluster.

.. note::  We assume that you know how to use Apache Spark and start a cluster. However, for the sake of demonstration the next two sections show how Spark can be easily started.

Local Spark context
....................

On a local resource, such as a laptop or PC, you would start the spark environment using:

.. code-block:: bash

  $SPARK_HOME/sbin/start-master.sh
  $SPARK_HOME/sbin/start-slave.sh <IP>

where ``$SPARK_HOME`` is the installation path of Spark and ``IP`` the IP to which we will submit jobs.

Cluster environment
....................

If you are working on a cluster, you can use the provided scripts to start a cluster.
**Make sure to have a working `openmpi` and `Java` installed**. We use ``sparkhpc``
in order to start a standalone cluster on an LSF/SGE high-performance computing cluster.

.. code-block:: bash

  ./0a-start-cluster.sh &
  ./0b-launch-cluster.sh &

.. note:: For your own cluster, you should modify the number of workers, nodes, cores and memory.

After the job has started, you need to call

.. code-block:: bash

  sparkcluster info

in order to receive the spark ``IP``.

Snakemake
~~~~~~~~~

If you made it thus far, you successfully

1) modified the config file,
2) started a Spark standalone cluster and have the ``IP`` to which the Spark cluster listens.

Now we can finally start our application.

.. code-block:: bash

  ./koios --configfile biospark-local.config
          --ip IP

That will run the dimension reduction, the outlier removal, the clustering and the analysis of the clusters.

You can also only run a subset of the targets.
For ``dimension-reduction``:

.. code-block:: bash

  ./koios --configfile biospark-local.config
          --ip IP
          dimension-reduction

For ``outlier-removal``:

.. code-block:: bash

  ./koios --configfile biospark-local.config
          --ip IP
          outlier-removal

For ``clustering``:

.. code-block:: bash

  ./koios --configfile biospark-local.config
          --ip IP
           clustering

In all cases, the respective plots and analyses are alywas run.