biospark
=============

.. image:: http://www.repostatus.org/badges/latest/active.svg
   :target: http://www.repostatus.org/#active
.. image:: https://travis-ci.org/cbg-ethz/biospark.svg?branch=master
   :target: https://travis-ci.org/cbg-ethz/biospark/
.. image:: https://codecov.io/gh/cbg-ethz/biospark/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/cbg-ethz/biospark
.. image:: https://api.codacy.com/project/badge/Grade/1822ba83768d4d7389ba667a9c839638
   :target: https://www.codacy.com/app/simon-dirmeier/rnaiutilities_2?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=cbg-ethz/rnaiutilities&amp;utm_campaign=Badge_Grade
.. image:: https://readthedocs.org/projects/biospark/badge/?version=latest
   :target: http://biospark.readthedocs.io/en/latest/
   :alt: doc


A library for analysis of big biological data sets using Snakemake and Apache Spark.

Introduction
------------

Welcome to ``biospark``.

``biospark`` is a Python/Scala library for analysis of big biological data sets.
We use Apache Spark as analytics engine for big data processing and machine learning,
and Snakemake for scheduling.

The library consists of the following steps:

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

1) Make sure to have ``python3`` installed. ``biospark`` does not support
previous versions. The best way to do that is to download `anaconda <https://www.continuum.io/downloads>`_ and create a
virtual `environment <https://conda.io/docs/using/envs.html>`_.

2) Download the latest `release <https://github.com/cbg-ethz/biospark/releases>`_ first and unpack it.

3) Install the required dependencies using:

.. code-block:: bash

  ./install_dependencies.sh

4) Install the Apache Spark from `here <https://spark.apache.org/downloads.html>`_ . Use the *prebuilt for Apache Hadoop* package type.

5) That is it.

Usage
-----

Using ``biospark`` requires providing a config file and starting a spark cluster.
We assume that you are familiar with using a spark standalone cluster, so we only briefly
discuss how the cluster is started.

Config
======

Your configuration file will need to have the following format:

.. literalinclude:: ../../biospark-local.config
  :caption: Contents of ``biospark-local.config`` file
  :name: biospark-local.config


The first line points to the ``spark-submit`` command which is provided by Apache Spark.
The second line contains the ``tsv`` with your data, while the third line is the *folder* where all outputs are saved to.
We use a factor analysis, PCA or kPCA for dimension reduction.
The number of latent features is determined by ``factors``.
The output of the dimension reduction will be used for clustering.
We apply a recursive clustering method that finds the optimal number of cluster
centers *K*. For this, you need to provide the maximal number of cluster centers,
since we use this as a reference point.
Finally ``sparkparams`` contains the parameters you want to provide spark with.
The Spark `documentation <https://spark.apache.org/docs/latest/submitting-applications.html>`_
for submitting applications provides details which arguments are valid here.

Spark
=====

In order for `biospark` to work you need to have a working
*standalone spark environment* set up, running and listening to some IP.
You can find a good introduction
 `here <https://spark.apache.org/docs/latest/spark-standalone.html>`_ on how
 to start the standalone Spark cluster.


Local Spark context
....................

On a local ressource, such as a laptop or PC, you would start the spark environment using:

.. code-block:: bash

  $SPARK_HOME/sbin/start-master.sh
  $SPARK_HOME/sbin/start-slave.sh <sparkip>

where ``$SPARK_HOME`` is the installation path of Spark.


#### Cluster environment

If you are working on a cluster, you can use the provided scripts to start a cluster.
 **Make sure to have a working `openmpi` and `java` installed**.

```bash
./0a-start-cluster.sh &
./0b-launch-cluster.sh &
```

### Running

Once you started the cluster, you start `snakemake`:

#### Local environment

```bash
snakemake -s biospark.snake --configfile biospark-local.config --config sparkip= <sparkip>
```

#### Cluster environment

```bash
snakemake -s biospark.snake --configfile biospark-grid.config --config sparkip= <sparkip>
```

That is it! This will create all required files in the data directory,
