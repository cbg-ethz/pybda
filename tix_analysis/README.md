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

## Author

* Simon Dirmeier <a href="mailto:simon.dirmeier@gmx.de">simon.dirmeier@gmx.de</a>
