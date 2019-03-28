Getting started
===============

*Getting started* walks you through the installation of koios and to submit your first program.
See the *examples* to get a better overview that koios has to offer.

Installation
------------

Installing PyBDA is easy.

1) Make sure to have ``python3`` installed. PyBDA does not support
   previous versions. The best way to do that is to download and install `anaconda <https://www.continuum.io/downloads>`_ and create a
   virtual `environment <https://conda.io/docs/using/envs.html>`_ like this:

   .. code-block:: bash

      conda create -y -n pybda python=3.6
      source activate pybda

.. note:: Make sure to use Python version 3.6 since some dependencies PyBDA uses so far don't work with versions 3.7 or 3.8.

2) Either install PyBDA from PyPI
   using

  .. code-block:: bash

     pip install pybda

  or by downloading the _latest_ `release <https://github.com/cbg-ethz/pybda/releases>`_

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
* and the ``IP`` to a running spark-cluster which runs the algorithms and methods to be executed. If no cluster
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
``spark``        path to Apache spark ``spark-submit`` executable
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

* ``factor_analysis`` `for factor analysis <https://en.wikipedia.org/wiki/Factor_analysis>`__,
* ``forest`` for `random forests <https://en.wikipedia.org/wiki/Random_forest>`__,
* ``gbm`` for stochastic `gradient boosting <https://en.wikipedia.org/wiki/Gradient_boosting>`__,
* ``glm`` for `generalized linear regression models <https://en.wikipedia.org/wiki/Generalized_linear_model>`__,
* ``gmm`` for `Gaussian mixture models <https://en.wikipedia.org/wiki/Mixture_model#Gaussian_mixture_model>`__,
* ``ica``  for `independent component analysis <https://en.wikipedia.org/wiki/Independent_component_analysis>`__,
* ``lda`` for `linear discriminant analysis <https://en.wikipedia.org/wiki/Linear_discriminant_analysis>`__,
* ``kmeans`` for `K-means <https://en.wikipedia.org/wiki/K-means_clustering>`__,
* ``kpca`` for `kernel principal component analysis <https://en.wikipedia.org/wiki/Kernel_principal_component_analysis>`__ using Fourier features to approximate the kernel map,
* ``pca`` for `principal component analysis <https://en.wikipedia.org/wiki/Principal_component_analysis>`__.

Example
.......

For instance, consider the config file below:

.. literalinclude:: ../../data/pybda-usecase.config
  :caption: Contents of ``data/pybda-usecase.config`` file
  :name: pybda-usecase.config

It would execute the following jobs:

1) dimension reduction (PCA) on the input file with 5 components,
2) clustering on the result of the dimensionality reduction with 3 cluster centers (``k``-means),
3) binomial-family generalized regression model (i.e. logistic) on the input file with response *is_infected* and features from ``data/feature_columns.tsv``

In addition we would allow Spark to use `3G` driver memory, `6G` executor memory and set the configuration variable ``spark.driver.maxResultSize``
to `3G` (all configurations can be found `here <https://spark.apache.org/docs/latest/configuration.html#available-properties>`__).

.. note:: PyBDA first parses through the config file and builds a DAG of the methods that should be executed. If it finds dimensionality reduction *and* clustering, it will first embed the data in a lower dimensional space und use the result of this for clustering (i.e. in order to remove correlated features). The same does *not* happen with regression.

Spark parameters
................

The Spark `documentation <https://spark.apache.org/docs/latest/submitting-applications.html>`__
for submitting applications provides details which arguments are valid here. You provide them as list in the yaml file as key ``sparkparams``:
Below, the most important two are listed:

``"--driver-memory=xG"``
    Amount of memory to use for the driver process in gigabyte, i.e. where SparkContext is initialized.

``"--executor-memory=xG"``
    Amount of memory to use per executor process in giga byte.

``"--conf spark.driver.maxResultSize=3G"``
    Limit of total size of serialized results of all partitions for each Spark action.

Spark
~~~~~~

In order for PyBDA to work you need to have a working
*standalone spark environment* set up, running and listening to some ``IP``.
You can find a good introduction
`here <https://spark.apache.org/docs/latest/spark-standalone.html>`__ on how
to start the standalone Spark cluster. Alternatively, as mentioned above, a desktop PC suffices as well, but will limit what PyBDA can do for you.

**We assume that you know how to use Apache Spark and start a cluster.**
However, for the sake of demonstration the next two sections give a short introduction how Spark clusters are set up.

Local Spark context
....................

On a local resource, such as a laptop or desktop computer, there is no need to start a Spark cluster.
In such a scenario the ``IP`` PyBDA requires for submitting jobs is just called ``local``.

Alternatively, you can always *simulate* a cluster environment. You start the Spark environment using:

.. code-block:: bash

  $SPARK_HOME/sbin/start-master.sh
  $SPARK_HOME/sbin/start-slave.sh <IP>

where ``$SPARK_HOME`` is the installation path of Spark and ``IP`` the IP to which we will submit jobs.
When calling ``start-master.sh`` Spark will log the ``IP`` it uses. Thus you need to have a look there to find it. Usually the line looks something like:

.. code-block:: bash

    2019-01-23 21:57:29 INFO  Master:54 - Starting Spark master at spark://<COMPUTERNAME>:7077

In the above case the ``IP`` is ``spark://<COMPUTERNAME>:7077``. Thus you start the slave using

.. code-block:: bash

    $SPARK_HOME/sbin/start-slave.sh spark://<COMPUTERNAME>:7077

That is it.

Cluster environment
....................

If you are working on a cluster, you can use ``sparkhpc`` to set up a Spark instance (find the documenation `here <https://sparkhpc.readthedocs.io/en/latest/>`__).

.. note:: If you want to use ``sparkhpc`` , please read its documentation to understand how Spark clusters are started.

Sparkhpc can be used to start a standalone cluster on an LSF/SGE high-performance computing environment. In order for them to work make sure to have
**openmpi and Java installed**. Sparkhpc installs with PyBDA, but in case it didn't just reinstall it:

.. code-block:: bash

  pip install sparkhpc

Sparkhpc helps you setting up spark clusters for LSF and Slurm cluster environments. If you have one of those start a Spark cluster, for instance, using:

.. code-block:: bash

  sparkcluster start --memory-per-executor 50000 --memory-per-core 10000 --walltime 4:00 --cores-per-executor 5 2 &
  sparkcluster launch &

.. warning:: For your own cluster, you should modify the number of workers, nodes, cores and memory.

In the above call we would request `2` nodes with `5` cores each. Every core would receive 10G of memory, while the entuire executor would receive `50G` of memory.

After the job has started, you need to call

.. code-block:: bash

  sparkcluster info

in order to receive the Spark ``IP``.

Calling
~~~~~~~

If you made it thus far, you successfully

1) modified the config file,
2) started a Spark standalone cluster and have the ``IP`` to which the Spark cluster listens.

Now we can finally start our application.

For dimension reduction:

.. code-block:: bash

  pybda dimension-reduction pybda-usecase.config IP

For clustering:

.. code-block:: bash

   pybda clustering pybda-usecase.config IP

For regression:

.. code-block:: bash

   pybda regression pybda-usecase.config IP

In all cases, the methods create ``tsv`` files, plots and statistics.

References
----------

Murphy, Kevin P. Machine learning: a probabilistic perspective. `MIT press` (2012).

Breiman, Leo. "Random forests." `Machine learning` 45.1 (2001): 5-32.

Friedman, Jerome H. "Stochastic gradient boosting." `Computational Statistics & Data Analysis` 38.4 (2002): 367-378.

Trevor, Hastie, Tibshirani Robert, and Friedman JH. "The elements of statistical learning: data mining, inference, and prediction." (2009).

Hyvärinen, Aapo, Juha Karhunen, and Erkki Oja. Independent component analysis. Vol. 46. `John Wiley & Sons` (2004).

Köster, Johannes, and Sven Rahmann. "Snakemake—a scalable bioinformatics workflow engine." `Bioinformatics` 28.19 (2012): 2520-2522.

Meng, Xiangrui, et al. "MLlib: Machine Learning in Apache Spark." `The Journal of Machine Learning Research` 17.1 (2016): 1235-1241

Rahimi, Ali, and Benjamin Recht. "Random features for large-scale kernel machines." `Advances in Neural Information Processing Systems` (2008).

Zaharia, Matei, et al. "Apache Spark: a unified engine for big data processing." `Communications of the ACM` 59.11 (2016): 56-65.

