Getting started
===============

*Getting started* walks you through the installation of koios and to submit your first program.
See the *examples* to get a better overview that koios has to offer.

Installation
------------

Installing ``koios`` is easy.

1) Make sure to have ``python3`` installed. ``koios`` does not support
   previous versions. The best way to do that is to download `anaconda <https://www.continuum.io/downloads>`_ and create a
   virtual `environment <https://conda.io/docs/using/envs.html>`_.

2) Either install ``koios`` from conda
   using

  .. code-block:: bash

     conda install koios -c conda-forge

  or from PYPI

  .. code-block:: bash

     pip install koios

  or by downloading the latest `release <https://github.com/cbg-ethz/biospark/releases>`_

  .. code-block:: bash

      tar -zxvf koios*.tar.gz
      pip install koios

  I obviously recommend installation using the first option.

3) Download Spark from `Apache Spark <https://spark.apache.org/downloads.html>`_ (use the *prebuilt for Apache Hadoop* package type)
   and install the unpacked folder into a custom path like ```opt/local/spark```. Put an alias into your ```.bashrc``` (or whatever shell you are using)

   .. code-block:: bash

      echo "alias spark-submit='opt/local/spark/bin/spark-submit'" >> .bashrc

4) That is it.


Usage
-----

Using ``koios`` requires providing two things:

* a config file that specifies the methods you want to use, paths to files, and parameters,
* and the IP to a running spark-cluster which runs the algorithms and methods to be executed. If no cluster
  environment is available you can also run koios locally. This, of course, somehow limits what koios can do for you,
  since it's real strength lies in distributed computation.

Config
~~~~~~~

Running koios requires a ``yaml`` configuration file that specifies several key-value pairs.
The config file consists of

* general arguments, such as file names,
* method specific arguments,
* arguments for Apache Spark.

General arguments
.................

The following table shows the arguments that are **mandatory** and need to be set in every application.

================ ================================================================
*Parameter*      *Explanation*
================ ================================================================
``spark``        path to Apache spark ``spark-submit`` exectuable
``infile``       tab-separated input file to use for any of the methods
``outfolder``    folder where all results are written to.
``meta``         names of the columns that represent meta information ("\n"-separated)
``features``     names of the columns that represent numerical features, i.e. columns that are used for analysis ("\n"-separated).
``sparkparams``  specifies parameters that are handed over to Apache Spark (which we cover in the section below)
================ ================================================================

Method specific arguments
.........................

The following tables show the arguments required for the single methods, i.e. dimension reduction,
clustering and regression.

+------------------------+--------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+
| *Method*               | *Options*                            |  *Method*                                                                                                                   |
+========================+======================================+=============================================================================================================================+
| **Dimension reduction**                                                                                                                                                                     |
+------------------------+--------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+
| ``dimension_reduction``| ``factor_analysis``/``pca``/``kpca`` | specifies which method to use for dimension reduction                                                                       |
+------------------------+--------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+
| ``n_components``       | e.g ``1,2,3`` or ``1``               | comma-separated list of integers specifying the number of variables in the lower dimensional space to use per reduction     |
+------------------------+--------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+
| **Clustering**                                                                                                                                                                              |
+------------------------+--------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+
| ``clustering``         | ``kmeans``/``gmm``                   | specifies which method to use for clustering                                                                                |
+------------------------+--------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+
| ``n_centers``          | e.g ``1,2,3`` or ``1``               | comma-separated list of integers specifying the number of clusters to use per cluystering                                   |
+------------------------+--------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+
| **Regression**                                                                                                                                                                              |
+------------------------+--------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+
| ``regression``         |  ``glm``/``forest``/``gbm``          | specifies which method to use for regression                                                                                |
+------------------------+--------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+
| ``response``           |                                      | name of column in ``infile`` that is the response                                                                           |
+------------------------+--------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+
| ``family``             | ``gaussian``/``binomial``            | distribution family of the response variable                                                                                |
+------------------------+--------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+

For instance, consider the config file below:

.. literalinclude:: ../../koios-usecase.config
  :caption: Contents of ``koios-usecase.config`` file
  :name: koios-usecase.config

It would execute the following jobs:

1) dimension reduction on the input file with 5 components -> clustering on the result of the dimensionality reduction with 3 cluster centers
2) binomial-family generalized regression model (i.e. logistic) on the input file with respone *is_infected*

.. note:: ``koios`` first parses through the config file and builds a DAG of the methods that should be executed. If it finds dimensionality reduction *and* clustering, it will first embed the data in a lower dimensional space und use the result of this for clustering (i.e. in order to remove correlated features). The same does *not* happen with regression.

Spark parameters
................

The Spark `documentation <https://spark.apache.org/docs/latest/submitting-applications.html>`_
for submitting applications provides details which arguments are valid here. You provide them as list in the yaml file as key ``sparkparams``:
Below, the most important two are listed:

``"--driver-memory=xG"``
    Amount of memory to use for the driver process in gigabyte, i.e. where SparkContext is initialized.

``"--executor-memory=xG"``
    Amount of memory to use per executor process in giga byte.

Spark
~~~~~~

In order for `koios` to work you need to have a working
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

  ./koios --configfile koios-usecase.config
          --ip IP
          dimension-reduction

For ``outlier-removal``:

.. code-block:: bash

  ./koios --configfile koios-usecase.config
          --ip IP
          outlier-removal

For ``clustering``:

.. code-block:: bash

  ./koios --configfile koios-usecase.config
          --ip IP
           clustering

In all cases, the respective plots and analyses are alywas run.