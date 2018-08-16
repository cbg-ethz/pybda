Use Case
========

Here we show a small use case of ``koios``. We prepared a sample data set
(``data/single_cell_samples.tsv``) which we use for analysis

Setting the config file
-----------------------

I use the following config files for the analysis.
Before I ran everything I do a test run using:

.. literalinclude:: ../../biospark-local.config
  :caption: Contents of ``biospark-local.config`` file
  :name: biospark-local-test.config

Starting the cluster
--------------------

First we start the cluster. Locally that would be done like this:

.. code-block:: bash

  $SPARK_HOME/sbin/start-master.sh
  $SPARK_HOME/sbin/start-slave.sh <IP>

Analysis
--------

Before we start analysing the data we do a dimension reduction into a 15-dimensional space using
``koios``.

.. code-block:: bash

  ./koios --configfile biospark-local.config
          --ip IP
          dimension-reduction

Youn will receive a couple of plots which you should check for Gaussianity.

Afterwards we use the outlier removal:

.. code-block:: bash

     ./koios --configfile biospark-local.config
          --ip IP
          outlier-removal

Finally we do the clustering:

.. code-block:: bash

     ./koios --configfile biospark-local.config
          --ip IP
          clustering

That's it. You get some plots to that which you should have a look at.