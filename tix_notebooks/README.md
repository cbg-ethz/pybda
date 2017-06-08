<h1 align="center"> tix notebooks </h1>

Collections of scripts for the data analysis using pyspark.

## Remote hpcnotebook

* Open a browser and change to SOCKS proxy port 9999.
* Submit a job like this

```sh
  bsub -R light -Is -n 4 -W 1:00 bash
```

* Then launch the notebook

```sh
  hpcnotebook launch
```


## Author

* Simon Dirmeier <a href="mailto:simon.dirmeier@gmx.de">simon.dirmeier@gmx.de</a>
