<h1 align="center"> tix notebooks </h1>

Collections of scripts for the data analysis using pyspark.

## Starting the sparkcluster

This is exactly how Rok describes it in the tutorials. ** DONT FORGET LOADING JAVA BEFORE**


## Remote hpcnotebook

* Open a browser and change to SOCKS proxy port 9999.
* Enable forwarding on your local machine

```sh
  ssh -Nf -D 9999 username@cluster >& ssh_errors
```

* Submit a job like this

```sh
  bsub -R light -Is -n 4 -W 1:00 bash
```

* Then launch the notebook **BUT DONT FORGET LOADING JAVA BEFORE**

```sh
  module load java
  hpcnotebook launch
```

## Spark examples


It seems that the pyspark api overwrites the command line configurations.
Although I should not set `driver-mermory` using `SparkConf` this overwriting still happens. I dont get it.

Options to submit:

1.

  ```python
    conf = pyspark.SparkConf().setMaster("local[*]") \
            .setAppName("test") \
            .set("spark.executor.memory", "2G")
    sc = pyspark.SparkContext(conf=conf)
  ```

  ```
    /usr/local/spark/spark/bin/spark-submit --driver-memory 20G ./tix_scripts/tix_normalize.py
  ```

2.

  ```python
    conf = pyspark.SparkConf().set("spark.master", "spark://10.205.17.48:7077").set("spark.executor.memory", "10G").set("spa
    sc = pyspark.SparkContext(conf=conf)
    spark = pyspark.sql.SparkSession(sc)
  ```

 ```¬
    /usr/local/spark/spark/bin/spark-submit --driver-memory 10G ./tix_scripts/tix_normalize.py¬
 ```

3.

  ```python
    conf = pyspark.SparkConf().set("spark.executor.memory", "10G").set("spa
    sc = pyspark.SparkContext(conf=conf)
    spark = pyspark.sql.SparkSession(sc)
  ```

 ```¬
    /usr/local/spark/spark/bin/spark-submit --master spark://10.205.18.36:7077  --driver-memory 10G ./tix_scripts/tix_normalize.py¬
 ```


## Author

* Simon Dirmeier <a href="mailto:simon.dirmeier@gmx.de">simon.dirmeier@gmx.de</a>
