Parser
------

TODO

Query
-----

TODO

.. code-block:: python

  # load the query module
  from rnaiutilities import Query
  # create a query object
  q = Query(<your db file>)
  # do a query
  res = q.query(library="d", featureclass="cells", gene="star", sample=10)
  # print to tsv
  res.dump("~/Desktop/bla.tsv")
