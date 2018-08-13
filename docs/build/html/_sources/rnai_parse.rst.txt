rnai-parse
----------

``rnai-parse`` parses Matlab files of image-based single-cell features
from RNAi screens. We assume the data has been generated using
``CellProfiler`` which creates a single file for each feature that can be
measured from a flourescence channel.

Usually from the matlab files features for a single cell are hard to access,
since they are distributed over the different files. With ``rnai-parse`` we
first iterate over the single feature files and combine the features into a
feature matrix that is easier to work with. The result is a single ``tsv`` file
for every plate where the rows are single-cells and the columns single-cell
features.

The following sections describe the usage of ``rnai-parse``, its
subcommands and the required *CONFIG* file. So far the following subcommands
are available:

* ``rnai-parse checkdownload`` for checking if all files are present correctly,
* ``rnai-parse parse`` for parsing the data,
* ``rnai-parse parsereport`` for creating a report of parsed files,
* ``rnai-parse featuresets`` for creating feature set overlap statistics.

**The subcommands are needed to be called consecutively.** So you need to
parse the files before creating reports and featureset statistics.


Introduction
............

To use ``rnai-parse``, you need to create a *CONFIG* file in ``yaml`` format
with the following content:


.. literalinclude:: ../../data/config.yml
  :caption: Contents of ``config.yml`` file
  :name: config.yml

You can have a look at an example yaml file `here <https://github.com/cbg-ethz/rnaiutilities/blob/master/data/config.yml>`_.


*layout_file* describes the placement of siRNAs and genes on the plates,
*plate_folder* points to the collection of matlab files, *output_path* is
the target directory where files are written to. *plate_id_file* is a list
of ids of plates that are going to be parsed in case only a subset of
*plate_folder* should get parsed. *plate_regex* is a pattern which plates you
want to use in the *plate_id*file*. *multiprocessing* is a boolean
determining whether python uses multiple processes or not.

Check out the `data`_ folder in the main repository for some example
datasets. The folder contains an example data-set for the pathogen
*S. Typhimurium*, the respective ``yaml`` config file, the meta file that
contains the plates to be parsed and the layout file for genes, sirnas, etc.

**For all subcommands only the config file is needed as an argument. So if you
create the file once, you are settled.**


Checking for file availability
..............................

As a first step it makes sense to check if all  plates from
your meta plate file (`experiment_meta_file.tsv`_) exist, i.e. have been
downloaded:

.. code-block:: bash

  rnai-parse checkdownload CONFIG


This just prints a report to ``stderr`` if the files exist or not.


Parsing the data
................

If the files are downloaded as intended, parse them to tsv:

.. code-block:: bash

  rnai-parse parse CONFIG

The result of the parsing process should be a set of files for every plate.
For example every plate should create ``*data.tsv`` files and a respective
``*meta.tsv`` for every data file. Every data file contains the features for
a specific channel, like DAPI.


Generating a report
...................

If parsing is complete, you can create a report if all files have been parsed
or if some are missing:


.. code-block:: bash

  rnai-parse parsereport CONFIG

The report is similar to ``rnai-parse checkdownload``, only that this time we
 check if every file has been parsed correctly and meta files have been
 created. Output is written to ``stderr``.


Computing overlapping feature sets
..................................

Finally after having done the parsing and file checking you can create
feature overlap statistics between the different screens like this:

.. code-block:: bash

  rnai-parse featuresets CONFIG

The script writes the results to ``stdout``.


.. _data: https://github.com/cbg-ethz/rnaiutilities/tree/master/data
.. _experiment_meta_file.tsv: https://github.com/cbg-ethz/rnaiutilities/tree/master/data/https://github.com/cbg-ethz/rnaiutilities/blob/master/data/experiment_meta_file.tsv