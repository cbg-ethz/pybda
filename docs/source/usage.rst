Getting started
===============

*Getting started* walks you through the installation of koios and to submit your first program.
See the *examples* to get a better overview that koios has to offer.

Installation
------------

Installing PyBDA is easy.

1) Make sure to have ``python3`` installed. PyBDA does not support
   previous versions. The best way to do that is to download `anaconda <https://www.continuum.io/downloads>`_ and create a
   virtual `environment <https://conda.io/docs/using/envs.html>`_.

2) Either install PyBDA from conda
   using

  .. code-block:: bash

     conda install pybda -c conda-forge

  or from PYPI

  .. code-block:: bash

     pip install pybda

  or by downloading the latest `release <https://github.com/cbg-ethz/biospark/releases>`_

  .. code-block:: bash

      tar -zxvf pybda*.tar.gz
      pip install pybda

  I obviously recommend installation using the first option.

3) Download Spark from `Apache Spark <https://spark.apache.org/downloads.html>`_ (use the *prebuilt for Apache Hadoop* package type)
   and install the unpacked folder into a custom path like ```opt/local/spark```. Put an alias into your ```.bashrc``` (or whatever shell you are using)

   .. code-block:: bash

      echo "alias spark-submit='opt/local/spark/bin/spark-submit'" >> .bashrc

4) That is it.


Usage
-----

Using PyBDA requires providing two things:

* a config file that specifies the methods you want to use, paths to files, and parameters,
* and the IP to a running spark-cluster which runs the algorithms and methods to be executed. If no cluster
  environment is available you can also run PyBDA locally. This, of course, somehow limits what PyBDA can do for you,
  since it's real strength lies in distributed computation.

Config
~~~~~~~

Running PyBDA requires a ``yaml`` configuration file that specifies several key-value pairs.
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

+------------------------+------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+
| *Parameter*            | *Argument*                                           |  *Explanation*                                                                                                              |
+========================+======================================================+=============================================================================================================================+
| **Dimension reduction**                                                                                                                                                                                     |
+------------------------+------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+
| ``dimension_reduction``| ``factor_analysis``/``pca``/``kpca``/``lda``/``ica`` | Specifies which method to use for dimension reduction                                                                       |
+------------------------+------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+
| ``n_components``       | e.g ``2,3,4`` or ``2``                               | Comma-separated list of integers specifying the number of variables in the lower dimensional space to use per reduction     |
+------------------------+------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+
| ``response``           | (only for ``lda``)                                   | Name of column in ``infile`` that is the response. Only required for linear discriminant analysis.                          |
+------------------------+------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+
| **Clustering**                                                                                                                                                                                              |
+------------------------+------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+
| ``clustering``         | ``kmeans``/``gmm``                                   | Specifies which method to use for clustering                                                                                |
+------------------------+------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+
| ``n_centers``          | e.g ``2,3,4`` or ``2``                               | Comma-separated list of integers specifying the number of clusters to use per cluystering                                   |
+------------------------+------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+
| **Regression**                                                                                                                                                                                              |
+------------------------+------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+
| ``regression``         |  ``glm``/``forest``/``gbm``                          | Specifies which method to use for regression                                                                                |
+------------------------+------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+
| ``response``                                                                  | Name of column in ``infile`` that is the response                                                                           |
+------------------------+------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+
| ``family``             | ``gaussian``/``binomial``/``categorical``            | Distribution family of the response variable                                                                                |
+------------------------+------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+

The abbreveations of the methods are explained in the following list.

* ``factor_analysis`` `for factor analysis <https://en.wikipedia.org/wiki/Factor_analysis>`_,
* ``forest`` for `random forests <https://en.wikipedia.org/wiki/Random_forest>`_ [RF]_,
* ``gbm`` for stochastic `gradient boosting <https://en.wikipedia.org/wiki/Gradient_boosting>`_ [SGB]_,
* ``glm`` for `generalized linear regression models <https://en.wikipedia.org/wiki/Generalized_linear_model>`_,
* ``gmm`` for `Gaussian mixture models <https://en.wikipedia.org/wiki/Mixture_model#Gaussian_mixture_model>`_,
* ``ica`` for `independent component analysis <https://en.wikipedia.org/wiki/Independent_component_analysis>`_,
* ``lda`` for `linear discriminant analysis <https://en.wikipedia.org/wiki/Linear_discriminant_analysis>`_,
* ``kmeans`` for `K-means <https://en.wikipedia.org/wiki/K-means_clustering>`_,
* ``kpca`` for `kernel principal component analysis <https://en.wikipedia.org/wiki/Kernel_principal_component_analysis>`_ using Fourier features [FF]_ to approximate the kernel.
* ``pca`` for `principal component analysis <https://en.wikipedia.org/wiki/Principal_component_analysis>`_,


Example
.......

For instance, consider the config file below:

.. literalinclude:: ../../pybda-usecase.config
  :caption: Contents of ``pybda-usecase.config`` file
  :name: pybda-usecase.config

It would execute the following jobs:

1) dimension reduction on the input file with 5 components -> clustering on the result of the dimensionality reduction with 3 cluster centers
2) binomial-family generalized regression model (i.e. logistic) on the input file with respone *is_infected*

.. note:: PyBDA first parses through the config file and builds a DAG of the methods that should be executed. If it finds dimensionality reduction *and* clustering, it will first embed the data in a lower dimensional space und use the result of this for clustering (i.e. in order to remove correlated features). The same does *not* happen with regression.

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

In order for PyBDA to work you need to have a working
*standalone spark environment* set up, running and listening to some ``IP``.
You can find a good introduction
`here <https://spark.apache.org/docs/latest/spark-standalone.html>`_ on how
to start the standalone Spark cluster. Alternatively, as mentioned above, a desktop PC suffices as well, but will limit what PyBDA can do for you.

We assume that you know how to use Apache Spark and start a cluster. However, for the sake of demonstration the next two sections show how Spark can be easily started.

Local Spark context
....................

On a local resource, such as a laptop or PC, there is no need to start a Spark cluster. In such a scenario the ``IP`` PyBDA requires for submitting jobs is just called ``local``.

Alternatively, you can always *simulate* a cluster environment. You would then start the spark environment using:

.. code-block:: bash

  $SPARK_HOME/sbin/start-master.sh
  $SPARK_HOME/sbin/start-slave.sh <IP>

where ``$SPARK_HOME`` is the installation path of Spark and ``IP`` the IP to which we will submit jobs.
When calling ``start-master.sh`` Spark will log the ``IP`` it uses. Thus you need to have a look there to find it. Usually the line looks something like:

.. code-block:: bash

    2019-01-23 21:57:29 INFO  Master:54 - Starting Spark master at spark://<COMPUTERNAME>:7077

In the above case the ``IP`` is ``spark://<COMPUTERNAME>:7077``.

Cluster environment
....................

If you are working on a cluster, you can use the provided scripts to start a cluster.
**Make sure to have a working ``openmpi`` and ``Java`` installed**. We use ``sparkhpc``
in order to start a standalone cluster on an LSF/SGE high-performance computing cluster.
Sparkhpc install with PyBDA, but in case it didn't just reinstall it:

.. code-block:: bash

  pip install sparkhpc

Sparkhpc helps you setting up spark clusters for LSF and Slurm cluster environments. If you have one of those start a Sparkcluster using:

.. code-block:: bash

  ./analysis/0a-start-cluster.sh &
  ./analysis/0b-launch-cluster.sh &

.. warning:: For your own cluster, you should modify the number of workers, nodes, cores and memory.

After the job has started, you need to call

.. code-block:: bash

  sparkcluster info

in order to receive the spark ``IP``.

Calling
~~~~~~~

If you made it thus far, you successfully

1) modified the config file,
2) started a Spark standalone cluster and have the ``IP`` to which the Spark cluster listens.

Now we can finally start our application.

For ``dimension-reduction``:

.. code-block:: bash

  pybda dimension-reduction pybda-usecase.config IP

For ``clustering``:

.. code-block:: bash

   pybda clustering pybda-usecase.config IP

For ``regression``:

.. code-block:: bash

   pybda regression pybda-usecase.config IP

In all cases, the methods create ``tsv`` files, plots and statistics.

References
----------

.. [FF] `Rahimi, Ali, and Benjamin Recht. "Random features for large-scale kernel machines." Advances in neural information processing systems. 2008. <http://papers.nips.cc/paper/3182-random-features-for-large-scale-kernel-machines.pdf>`_
.. [SGB] `Friedman, Jerome H. "Stochastic gradient boosting." Computational Statistics & Data Analysis 38.4 (2002): 367-378 <https://doi.org/10.1016/S0167-9473(01)00065-2>`_.
.. [RF] `Breiman, Leo. "Random forests." Machine learning 45.1 (2001): 5-32. <https://doi.org/10.1023/A:1010933404324>`_