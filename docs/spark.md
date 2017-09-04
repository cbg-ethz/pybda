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
  module load open_mpi
  hpcnotebook launch
```

## Sparkcluster


```sh
  module load java
  module load open_mpi
  sparkcluster .... start
  sparkcluster launch
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

## Submission


```bash
  sparkcluster start  --memory-per-executor 10000 --memory-per-core 1000 10

  sparkcluster launch --memory 5G --cores-per-executor 10
  sparkcluster launch --memory 500G --cores-per-executor 20
  sparkcluster launch --timeout 10 --memory 500G --cores-per-executor 20

  /cluster/home/simondi/spark/bin/spark-submit  --master spark://10.205.0.132:7077  tix_cluster.py

  #working: no memory at all: only executors
  /cluster/home/simondi/spark/bin/spark-submit  --master spark://10.205.0
  .134:7077  --num-executors 2 --executor-cores 10  tix_scripts/tix_cluster.py
```

```
  sparkcluster start --memory-per-executor 15000 --memory-per-core 10000
    --walltime 4:00 --cores-per-executor 1  20

   # DO NOT GO OVER LIMITS
  sparkcluster launch --memory 190G --timeout 1000 --cores-per-executor 2

  # DO NOT GO OVER LIMTITS
  /cluster/home/simondi/spark/bin/spark-submit  --master spark://10.205.0.129:7078
    --num-executors 20 --executor-cores 1  tix_scripts/tix_cluster.py
```

```
    # take all memory: give one core per executor
 sparkcluster launch --timeout 10 --memory 100G --cores-per-executor 1

```

# Working solution for SINGLE core: how is this extended to many?

```
    # seems to work: single core exe
     sparkcluster start --memory-per-executor 15000 --memory-per-core 10000 --walltime 4:00 --cores-per-executor 1  20
    sparkcluster launch --memory 190G --timeout 10

    /cluster/home/simondi/spark/bin/spark-submit  --master spark://10.205.0.129:7078
       --num-executors 20 --executor-cores 1  --total-executor-cores 20
      tix_scripts/tix_cluster.py


## Author

* Simon Dirmeier <a href="mailto:simon.dirmeier@gmx.de">simon.dirmeier@gmx.de</a>
