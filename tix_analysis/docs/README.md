## Spark examples

1.

```python
  conf = pyspark.SparkConf().setMaster("local[*]") \
          .setAppName("test") \
          .set("spark.driver.memory", "2G") \
          .set("spark.executor.memory", "2G")
  sc = pyspark.SparkContext(conf=conf)
```

```
  /usr/local/spark/spark/bin/spark-submit --master local ./tix_scripts/tix_normalize.py
```
