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


Your first program
------------------

Using ``koios`` requires providing a config-file and starting a spark-cluster to which the jobs,
i.e. the methods you want to use, are sent to and executed. If no cluster is available, you can
also use your local desktop computer. This, of course, somehow limits what ``koios`` can do for you,
since it's real strength lies in distributed computation.

Let's start with an introductory example

Config
~~~~~~~

Your configuration file will need to have the following format:

.. literalinclude:: ../../koios-usecase.config
  :caption: Contents of ``koios-usecase.config`` file
  :name: koios-usecase.config

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