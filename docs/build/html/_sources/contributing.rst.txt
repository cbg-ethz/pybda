Contributing
============

We welcome pull requests and contributions to make PyBDA a community driven tool
for big data analytics.

You can contribute in the following ways:

* improve the documentation,
* add custom methods or algorithms,
* report bugs,
* improve general usability or speed up code,
* write unit tests.

How to contribute
-----------------

In order to make a contribution best follow these steps:

* Create a fork of the repository on `GitHub <https://github.com/cbg-ethz/pybda>`__.
* Checkout the ``develop`` branch and create your own branch using

  .. code-block:: bash

    git checkout develop
    git checkout -b myfeature

* Install all dependencies using ``pip install '.[dev]'``.
* Add your feature and submit a pull request.

Coding standards
----------------

Please format your code using ``yapf`` and ``flake8``:

.. code-block:: bash

    cd pybda
    yapf --style ../.styles.yapf -i my_file.py
    tox -e lint

Furthermore, please don't duplicate code and try to use type annotations where you
find them necessary or useful.
