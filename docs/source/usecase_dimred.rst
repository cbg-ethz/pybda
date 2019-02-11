Dimension reduction
===================

Here we show a small use case of how to do a dimension reduction on a small sample data set
(``data/single_cell_samples.tsv``). We assume you
already set up the cluster for Spark (other check `here <./usage.html#spark>`_) with
an ``IP`` address.

Analysis
--------

For analysis we decide use a kernel PCA to map data into a lower dimensional space.
Koios offers in total three ways to do dimension reduction:

* ``pca`` for `principal component analysis <https://en.wikipedia.org/wiki/Principal_component_analysis>`_,
* ``factor_analysis`` `for factor analysis <https://en.wikipedia.org/wiki/Factor_analysis>`_,
* ``kpca`` for `kernel principal component analysis <https://en.wikipedia.org/wiki/Kernel_principal_component_analysis>`_ using Fourier features [FF]_ to approximate the kernel.

The config file we need to specify is in this case rather concise:

.. literalinclude:: ../../pybda-usecase-kpca.config
  :caption: Contents of ``pybda-usecase-kpca.config`` file
  :name: pybda-usecase-kpca.config

In the config above we will do the following:

* Use a kpca to map the data set into a two-dimensional space,
* give the Spark driver $3G$ of memory and the executor $6G$ of memory.

Having the parameters set, we call PyBDA

.. code-block:: bash

  pybda dimension-reduction pybda-usecase-kpca.config IP
