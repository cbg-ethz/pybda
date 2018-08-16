Big data analysis
=================

This document describes the workflow for the data analysis of the *TargetInfectX* (TiX) project.
The TiX project consists of single-cell microscopy images of multiple channels.
Cells have been grown on 384 well plates and been knocked down using RNA interference.
Afterwards cells have been infected with different pathogens.
The resulting data has measurements of cell features, nuclei features, pathogenic features, etc.

Parsing
-------

We started by downloading the complete data-set of features as extracted from the i
mages using `CellProfiler <http://cellprofiler.org/>`_.
Subsequently we do some preprocessing using our in-house python tool
`rnaiutilities <https://cbg-ethz.github.io/rnaiutilities/>`_.

First we check for the correct number of downloads:

.. code-block:: bash

  rnai-parse checkdownload /path/config_leonhard.yml

This should give some files that are **not** downloaded.
These are indeed **empty** on the
`openBIS <https://infectx.biozentrum.unibas.ch/openbis/>`_ instance from which we
downloaded the data.

Afterwards we parse the files using:

.. code-block:: bash

  rnai-parse parse /path/config_leonhard.yml

Having parsed all files, we can check fif everything went as expected by creating a download report:

.. code-block:: bash

  rnai-parse report /path/config_leonhard.yml

Furthermore, to see which feature-sets make most sense to take,
we can compute pairwise Jaccard indexes between the feature sets. We need that,
because the different experiments in the data sets don't have the same features.

.. code-block:: bash

  rnai-parse featuresets /path/config_leonhard.yml


Preprocessing
-------------

Next the parsed data's meta information are stored in a indexed data-based in
order to quickly retrieve plate information. The mentioned files are found in the
``results/1-preprocessing/0-features/current_analysis`` folder.
The entry to this part is ``featuresets_feature_files.tsv``
which has been created using ``rnai-parse featuresets``.

First we created a index for the complete data-set using ``sqlite``:

.. code-block:: bash

  rnai-query insert
             --db /path/to/tix_index.db
             /path/screening_data


Then create the feature sets created from calling
``rnai-parse featuresets`` (from terminal):

.. code-block:: bash

  ./0-create_maximal_feature_sets.py featuresets_feature_files.tsv > feature_sets_max.tsv


Create plots (`feature_overlap.eps` and `feature_histogram.eps`)
from the files created during the step (from terminal).

.. code-block:: bash

  ./1-plot_featuresets.R


Print the plates with maximal feature sets (from terminal):

.. code-block:: bash

  ./2-extract_plates_from_screens.py experiment_meta_file.tsv feature_sets_max.tsv 100 > feature_plates_and_screens_100.tsv
  ./2-extract_plates_from_screens.py experiment_meta_file.tsv feature_sets_max.tsv 250 > feature_plates_and_screens_250.tsv
  ./2-extract_plates_from_screens.py experiment_meta_file.tsv feature_sets_max.tsv 500 > feature_plates_and_screens_500.tsv


Parse the file created above (from terminal):

.. code-block:: bash

  ./3-plate_names.awk feature_plates_and_screens_x.tsv > feature_plate_names_x.tsv

.. code-block:: bash

  ./4-get_file_sets_from_db.sh feature_plate_names_x.tsv feature_dbq_x.tsv.tsv


The last file (`feature_dbq_x.tsv`) can be used with `rnai-query compose` to get the data from the database (from *leonhard*):

.. code-block:: bash

  ./5-rnai_query.sh 10/100/1000 feature_dbq_250.tsv


After that you should plots the reults of `rnai-query` to make sure your data is approximately Gaussian.
I recommend to do querying on only 10 cells, too, such that plotting is easier

.. code-block:: bash

  ./6-plot_feature_distribution.R 100/1000 feature_dbq_250.tsv


Setting the config file
-----------------------

I use the following config files for the analysis.
Before I ran everything I do a test run using:

.. literalinclude:: ../../biospark-grid-test.config
  :caption: Contents of ``biospark-grid-test.config`` file
  :name: biospark-grid-test.config

The config of the main run looks like this:

.. literalinclude:: ../../biospark-grid.config
  :caption: Contents of ``biospark-grid.config`` file
  :name: biospark-grid.config


Staring the cluster
-------------------

First we start the cluster. Locally that would be done like this:

.. code-block:: bash

  $SPARK_HOME/sbin/start-master.sh
  $SPARK_HOME/sbin/start-slave.sh <IP>

In a cluster environment, this is the command to be executed:

.. code-block:: bash

    module load jdk/8u92
    module load openmpi/2.1.0

    ./0a-start_cluster.sh
    ./0b-launch_cluster.sh

    sparkcluster info

.. note:: ``openmpi`` and ``java`` needs to be loaded on every shell session.

Analysis
--------

Before we start analysing the data we do a dimension reduction into a 15-dimensional space using
``koios``.
The input file is a data set created using ``rnai-query compose`` (see above).
The output is a parquet folder.

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