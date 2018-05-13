## Biospark

> biospark:  a `snakemake` pipeline for analysis of biological big-data screens using `spark`

## Dependencies

Make sure to have `spark >= 2.2.0` and all the dependencies given in `requirements.txt` installed.

# TODO: add r requirements

## Usage

### Config

We start by configuring the config file `biospark.config`:

```bash
spark: /usr/local/spark/spark/bin/spark-submit
infile: data/single_cell_samples.tsv
outfolder: data
factors: 15
centers: 2,5,10
sparkparams:
  - "--driver-memory=3G"
  - "--executor-memory=6G"
```

Here, you only need to change the infile parameter, the folder where you want to save the results and the number of cluster centers we want to test.

### Spark

In order for `biospark` to work you need to have a working *standalone spark environment* already set up and running. This part needs to be done by the user. You can find a good introduction [here](https://spark.apache.org/docs/latest/spark-standalone.html).

If you started your local spark context, you will receive the IP of the master, fo instance something like: `spark://5.6.7.8:7077`.

#### Local environment

On a laptop you would start the spark environment using:

```bash
$SPARK_HOME/sbin/start-master.sh
$SPARK_HOME/sbin/start-slave.sh <sparkip>
```

#### Cluster environment

If you are working on a cluster, I recommend using `sparkhpc` to start a cluster. You can use the provided scripts to start a cluster. **Make sure to have a working `openmpi` and `java` installed**.

```bash
./0a-start-cluster.sh &
./0b-launch-cluster.sh &
```

### Running

Once you started the cluster, you start `snakemake`:

```bash
snakemake -s biospark.snake --configfile biospark-local.config --config sparkip= <sparkip>
```

That is it! This will create all required files in the data directory,
