## Biospark

> biospark:  a `snakemake` pipeline for analysis of biological big-data screens using `spark`

## Dependencies

Make sure to have `spark >= 2.2.0` and all the dependencies given in `requirements.txt`
installed.

## Usage

### Config

We start by configuring the config file `biospark.config`:

```bash
infile:
    - data/single_cell_samples.tsv
outfolder:
    - data
centers:
    - 2,3,4,5,6
```

Here, you only need to change the infile parameter, the folder where you want to save the results and the number of cluster centers we want to test.

### Spark

In order for `biospark` to work you need to have a working *standalone spark environment* already set up and running. This part needs to be done by the user. You can find a good introduction [here](https://spark.apache.org/docs/latest/spark-standalone.html).

If you started your local spark context, you will receive the IP of the master, fo instance something like: `spark://5.6.7.8:7077`.

#### Local environment

On a laptop you would start the spark environment using:

```bash
$SPARK_HOME/sbin/start-master.sh
```

#### Cluster environment



### Running

Once you started the cluster, you start `snakemake`:

```bash
snakemake -s biospark.snake --config spark=IP
```

That is it! This will create all required files in the data directory,
