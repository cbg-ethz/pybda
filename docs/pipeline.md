# TargetInfectX data analysis

This document describes the steps taken for the data analysis of the *TargetInfectX* project.

## Preprocessing

We first downloaded the complete data-set using the `BeeDataDownloader`. Subsequently we do some preprocessing using our in-house python tool `rnaitutilities`.

First we check for the correct number of downloads:

```python 
  rnai-parse checkdownload /cluster/home/simondi/PROJECTS/config_leonhard.yml
```

This should give some files that are **not** downloaded. These are indeed **empty on the openBIS instance**.

Afterwards we parse the files using:

```python
  rnai-parse parse /cluster/home/simondi/PROJECTS/config_leonhard.yml
```

Having parsed all files, we can check fif everything went as expected by creating a download report:

```python
  rnai-parse report /cluster/home/simondi/PROJECTS/config_leonhard.yml
```

Furthermore, to see which feature-sets make most sense to take, we can compute pairwise Jaccard indexes between the feature sets using:

```python
  rnai-parse featuresets /cluster/home/simondi/PROJECTS/config_leonhard.yml
```

For this analysis we decided to exlcude the following plates:

* all quiagen plates (different features)
* all bartonella plates (has invasomes)
* brucella-qu-g1-h28[123]-13 (missing online)
* salmonella-dp-g1-dz{01-57}-2e (missing online)
