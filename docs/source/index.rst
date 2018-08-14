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


Installation
------------

Make sure to have ``python3`` installed. ``biospark`` does not support
previous versions. The best way to do that is to download `anaconda <https://www.continuum.io/downloads>`_ and create a
virtual `environment <https://conda.io/docs/using/envs.html>`_.

Download the latest `release <https://github.com/cbg-ethz/biospark/releases>`_ first and install it using:

//# TODOD


Usage
-----

## Dependencies

Make sure to have `spark >= 2.2.0` and all the dependencies given in `requirements.txt` installed.

# TODO: add r requirements

`org.Hs.eg.db`
`hgu95av2.db`

## Usage

### Config

We start by configuring the config file `biospark.config`:

```bash
spark: /usr/local/spark/spark/bin/spark-submit
infile: data/single_cell_samples.tsv
outfolder: data
factors: 15
centers:
  - 2
  - 5
sparkparams:
  - "--driver-memory=3G"
  - "--executor-memory=6G"
```

Here, you only need to change the infile parameter, the folder where you want to save the results and the number of cluster centers we want to test.

### Spark

In order for `biospark` to work you need to have a working *standalone spark environment* already set up and running. This part needs to be done by the user. You can find a good introduction [here](https://spark.apache.org/docs/latest/spark-standalone.html).

If you started your local spark context, you will receive the IP of the master, fo instance something like: `spark://5.6.7.8:7077`.

#### Local environment

On a laptop you would start the spark environment using:

```bash
$SPARK_HOME/sbin/start-master.sh
$SPARK_HOME/sbin/start-slave.sh <sparkip>
```

#### Cluster environment

If you are working on a cluster, I recommend using `sparkhpc` to start a cluster. You can use the provided scripts to start a cluster. **Make sure to have a working `openmpi` and `java` installed**.

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
