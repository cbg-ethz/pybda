Examples
========

The following section shows some use cases on how to use PyBDA.

Dimension reduction
-------------------

Here we show a small use case of how to do a dimension reduction on a small sample data set
(``data/iris.tsv``). We assume you
already set up the cluster for Spark (other check `here <./usage.html#spark>`__) with
an ``IP`` address.

Analysis
........

For analysis we decide use a linear discriminant analysis to map data into a lower dimensional space.
PyBDA offers the following methods to do dimension reduction:

* ``pca`` for `principal component analysis <https://en.wikipedia.org/wiki/Principal_component_analysis>`__,
* ``factor_analysis`` `for factor analysis <https://en.wikipedia.org/wiki/Factor_analysis>`__,
* ``kpca`` for `kernel principal component analysis <https://en.wikipedia.org/wiki/Kernel_principal_component_analysis>`_ using Fourier features to approximate the kernel,
* ``lda`` for `linear discriminant analysis <https://en.wikipedia.org/wiki/Linear_discriminant_analysis>`__,
* ``ica`` for `independent component analysis <https://en.wikipedia.org/wiki/Independent_component_analysis>`__.

The config file we need to specify is in this case rather concise:

.. literalinclude:: ../../data/pybda-usecase-dimred.config
  :caption: Contents of ``data/pybda-usecase-dimred.config`` file
  :name: pybda-usecase-dimred.config

In the config above we will do the following:

* Use a linear discriminant analysis to map the data set into a two-dimensional space using ``Species`` as a response.
* give the Spark driver 1G of memory and the executor 1G of memory.

Having the parameters set, we call PyBDA

.. code-block:: bash

  pybda dimension-reduction pybda-usecase-dimred.config IP

Clustering
----------

Here we show a small use case of how to cluster data on a small sample data set
(``data/iris.tsv``). We assume you
already set up the cluster for Spark (other check `here <./usage.html#spark>`__) with an ``IP`` address.

Analysis
........

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

Regression
----------

Here we show a small use case of how to regress a variable onto another set of variables exemplified
on a small sample data set (``data/iris.tsv``). We assume you
already set up the cluster for Spark (other check `here <./usage.html#spark>`__) with
an ``IP`` address.

Analysis
........

We will use a generalized linear regression model to establish a dependency between
a response and a set of predictors. Apart to the GLM, you can choose from
several regression methods

* ``glm`` for `generalized linear regression models <https://en.wikipedia.org/wiki/Generalized_linear_model>`__,
* ``gbm`` for stochastic `gradient boosting <https://en.wikipedia.org/wiki/Gradient_boosting>`__ ,
* ``forest`` for `random forests <https://en.wikipedia.org/wiki/Random_forest>`__ .

The config file we need to specify is in this case rather concise:

.. literalinclude:: ../../data/pybda-usecase-regression.config
  :caption: Contents of ``data/pybda-usecase-regression.config`` file
  :name: pybda-usecase-regression.config

In the config above we will do the following:

* Use a generalized linear regression model with logit-link,
* take as response the column called ``log_response``,
* predict the response of for the same data set,
* give the Spark driver 1G of memory and the executor 1G of memory,
* set the Spark configuration variable ``spark.driver.maxResultSize`` to 1G

Having the parameters set, we call PyBDA

.. code-block:: bash

  pybda dimension-reduction pybda-usecase-kpca.config IP
