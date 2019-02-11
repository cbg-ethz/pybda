Regression
==========

Here we show a small use case of how to regress a variable onto another set of variables exemplified
on a small sample data set (``data/single_cell_samples.tsv``). We assume you
already set up the cluster for Spark (other check `here <./usage.html#spark>`_) with
an ``IP`` address.

Analysis
--------

We will use a generalized linear regression model to establish a dependency between
a response and a set of predictors. Apart to the GLM, you can overall choose from
several regression methods

* ``glm`` for `generalized linear regression models <https://en.wikipedia.org/wiki/Generalized_linear_model>`_,
* ``gbm`` for stochastic `gradient boosting <https://en.wikipedia.org/wiki/Gradient_boosting>`_ [SGB]_,
* ``forest`` for `random forests <https://en.wikipedia.org/wiki/Random_forest>`_ [RF]_.

The config file we need to specify is in this case rather concise:

.. literalinclude:: ../../pybda-usecase-logreg.config
  :caption: Contents of ``pybda-usecase-logreg.config`` file
  :name: pybda-usecase-logreg.config

In the config above we will do the following:

* Use a kpca to map the data set into a two-dimensional space,
* give the Spark driver $3G$ of memory and the executor $6G$ of memory.

Having the parameters set, we call PyBDA

.. code-block:: bash

  pybda dimension-reduction pybda-usecase-kpca.config IP
