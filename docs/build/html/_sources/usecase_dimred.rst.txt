Dimension reduction
===================

Here we show a small use case of how to do a dimension reduction on a small sample data set
(``data/iris.tsv``). We assume you
already set up the cluster for Spark (other check `here <./usage.html#spark>`__) with
an ``IP`` address.

Analysis
--------

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
