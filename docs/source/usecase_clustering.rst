Clustering
==========

Here we show a small use case of how to cluster data on a small sample data set
(``data/iris.tsv``). We assume you
already set up the cluster for Spark (other check `here <./usage.html#spark>`__) with an ``IP`` address.

Analysis
--------

For analysis we decide to use a simple k-means with various cluster centers. All
methods for clustering are:

* ``kmeans`` for `K-means <https://en.wikipedia.org/wiki/K-means_clustering>`__,
* ``gmm`` for `Gaussian mixture models <https://en.wikipedia.org/wiki/Mixture_model#Gaussian_mixture_model>`__.

In order to account for correlated features, we first map the features into a lower
dimensional space using factor analysis (we could also use a GMM, where we estimate
the correlations too, or remove the line in the config):

.. literalinclude:: ../../data/pybda-usecase-clustering.config
  :caption: Contents of ``data/pybda-usecase-clustering.config`` file
  :name: pybda-usecase-clustering.config

In the config above we will do the following.

* Use a factor analysis into a space with two dimensions on the features in ``data/iris_feature_columns.tsv``,
* do a clustering with 2, 3 and 5 cluster centers on the two features we got from the factor analysis,
* give the Spark driver 3G of memory and the executor 1G of memory.

Having the parameters set, we call PyBDA

.. code-block:: bash

  pybda clustering pybda-usecase-clustering.config ``IP``

The above command first executes the dimension reduction and then the clustering.
After both ran, you should check the plots and statistics.