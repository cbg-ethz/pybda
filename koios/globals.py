# Copyright (C) 2018 Simon Dirmeier
#
# This file is part of koios.
#
# koios is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# koios is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with koios. If not, see <http://www.gnu.org/licenses/>.
#
# @author = 'Simon Dirmeier'
# @email = 'simon.dirmeier@bsse.ethz.ch'


import collections

LOGLIK_ = "loglik"
NULL_LOGLIK_ = "null_" + LOGLIK_
WITHIN_VAR_ = "within_cluster_variance"
TOTAL_VAR_ = "total_variance"
EXPL_VAR_ = "explained_variance"
N_, P_, K_ = "n", "p", "k"
BIC_ = "BIC"
NULL_BIC_ = "null_" + BIC_
PATH_ = "path"

PLOT_FONT_ = "Tahoma"
PLOT_FONT_FAMILY_ = 'sans-serif'
PLOT_STYLE_ = "seaborn-whitegrid"
RED_ = "#990000"

DOUBLE_ = "double"
FLOAT_ = "float"
FLOAT32_ = "float64"
FLOAT64_ = "float32"
TSV_ = "tsv"

FEATURES_ = "features"
GAUSSIAN_ = "gaussian"
BINOMIAL_ = "binomial"

DEBUG__ = "debug"
SPARK__ = "spark"
SPARKIP__ = SPARK__ + "ip"
SPARKPARAMS__ = SPARK__ + "params"
INFILE__ = "infile"
OUTFOLDER__ = "outfolder"

PVAL__ = "pvalue"
META__ = "meta"
FEATURES__ = "features"
RESPONSE__ = "response"

DIM_RED__ = "dimension_reduction"
DIM_RED_INFILE__ = DIM_RED__ + "_" + INFILE__
PCA__ = "pca"
KPCA__ = "kpca"
FACTOR_ANALYSIS__ = "factor_analysis"
N_COMPONENTS__ = "n_components"

OUTLIERS__ = "outliers"
OUTLIERS_INFILE__ = OUTLIERS__ + "_" + INFILE__
MAHA__ = "mahalanobis"

PREDICT__ = "predict"
CLUSTERING__ = "clustering"
CLUSTERING_INFILE__ = CLUSTERING__ + "_" + INFILE__
KMEANS__ = "kmeans"
GMM__ = "gmm"
MAX_CENTERS__ = "max_centers"
N_CENTERS__ = "n_centers"
RESPONSIBILITIES__ = "responsibilities"
RAW_PREDICTION__ = "rawPrediction"
PROBABILITY__ = "probability"

REGRESSION__ = "regression"
REGRESSION_INFILE__ = REGRESSION__ + "_" + INFILE__
GLM__ = "glm"
GBM__ = "gbm"
FOREST__ = "forest"
FAMILY__ = "family"

RULE_INFILE__ = "rule" + "_" + INFILE__

REQUIRED_ARGS__ = [
    SPARK__,
    INFILE__,
    OUTFOLDER__
]

PREPROCESSING_METHODS__ = [DIM_RED__, OUTLIERS__]
METHODS__ = PREPROCESSING_METHODS__ + [CLUSTERING__, REGRESSION__]
PARENT_METHODS__ = collections.OrderedDict(
  [
      (CLUSTERING__, PREPROCESSING_METHODS__),
      (REGRESSION__, None)
  ]
)
