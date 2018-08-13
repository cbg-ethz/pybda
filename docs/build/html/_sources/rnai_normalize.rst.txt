rnai-normalize
--------------

``rnai-normalize`` performs normalization of the compiled data-sets (see
:doc:`rnai_query`). Usually, RNA interference screens suffer from batch
effects that have to be corrected for.

``rnai-normalize`` so far only *standardizes* the data-set. We hope to extend
 the method soon...

The following sections explain the tool's usage.


Normalizing data by standardization
...................................

In order to normalize your data-set, just call:

.. code-block:: bash

  rnai-normalize i_am_the_result_from_rnai_query.tsv

That's it.
