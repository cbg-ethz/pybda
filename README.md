<h1 align="center"> tix-analysis </h1>

[![Project Status](http://www.repostatus.org/badges/latest/wip.svg)](http://www.repostatus.org/#wip)

Analysis of big RNAi data-sets in Python.

## Introduction

This repository contains `python` modules, `Jupyter notebooks` and other utility scripts for anlaysis of big image-based single-cell RNAi data-sets.
The methods depend on `Spark` for distributed high-performance resources. 

## Dependencies

You need to have `Python >= 3` installed, as well as a recent `Spark` installation in your `$HOME` folder. 
Otherwise a softlink should also suffice.

Install the required packages using:

```bash
  pip install -r requirements.txt
```

That should be all you need. 

## Files and folders

#### Numbered folders

This is the pipeline followed for analysis. Check out the folders' `README.md`s.

#### Docs

Collection of documentation files how to run `Spark` and the summary of the analysis (`pipeline`).

## Author

* Simon Dirmeier <a href="mailto:simon.dirmeier@gmx.de">simon.dirmeier@gmx.de</a>
