# Κοῖος /ˈci.os/ <img src="https://github.com/cbg-ethz/koios/blob/develop/fig/sticker_koios.png" align="right" width="160px"/>

[![Project Status](http://www.repostatus.org/badges/latest/wip.svg)](http://www.repostatus.org/#wip)
[![Build Status](https://travis-ci.org/cbg-ethz/koios.svg?branch=master)](https://travis-ci.org/cbg-ethz/koios/)
[![codecov](https://codecov.io/gh/cbg-ethz/koios/branch/master/graph/badge.svg)](https://codecov.io/gh/cbg-ethz/koios)
[![codedacy](https://api.codacy.com/project/badge/Grade/1822ba83768d4d7389ba667a9c839638)](https://www.codacy.com/app/simon-dirmeier/rnaiutilities_2?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=cbg-ethz/koios&amp;utm_campaign=Badge_Grade)
[![readthedocs](https://readthedocs.org/projects/koios/badge/?version=latest)](http://koios.readthedocs.io/en/latest)

A library for analysis of big biological data sets using Snakemake, powered by Apache Spark.

## Introduction

`koios` is a Python/Scala library for analysis of big biological data sets.
We use Apache Spark as analytics engine for data processing and machine learning,
and Snakemake for scheduling.

<div align="center" style="margin: 2%;">
	<p><b>The <i>koios</i></b> pipeline.</p>
  <img src="https://rawgit.com/cbg-ethz/koios/develop/fig/snakeflow.svg" alt="Drawing" width="50%" />
</div>

With `koios` you can easily

* preprocess your data with dimension reduction and outlier removal,
* analyse it using clustering or regression,
* create visualizations and critize what you've found.

## Documentation

Check out the documentation [here](https://cbg-ethz.github.io/koios/index.html).
The documentation will walk you though

* the required dependencies,
* the installation process,
* setting up Apache Spark,
* using `koios`.

## Author

Simon Dirmeier <a href="mailto:simon.dirmeier@bsse.ethz.ch">simon.dirmeier@bsse.ethz.ch</a>
