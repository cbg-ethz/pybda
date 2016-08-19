Regression
==========

Here we show a small use case of how to regress a variable onto another set of variables exemplified
on a small sample data set (``data/iris.tsv``). We assume you
already set up the cluster for Spark (other check `here <./usage.html#spark>`__) with
an ``IP`` address.

Analysis
--------

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
