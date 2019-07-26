# Copyright (C) 2018, 2019 Simon Dirmeier
#
# This file is part of pybda.
#
# pybda is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pybda is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pybda. If not, see <http://www.gnu.org/licenses/>.
#
# @author = 'Simon Dirmeier'
# @email = 'simon.dirmeier@bsse.ethz.ch'


import collections

BIC_ = "BIC"
BINOMIAL_ = "binomial"
CLUSTERING__ = "clustering"
DEBUG__ = "debug"
DIM_RED__ = "dimension_reduction"
DOUBLE_ = "double"
EXPL_VAR_ = "explained_variance"
FACTOR_ANALYSIS__ = "factor_analysis"
FAMILY__ = "family"
FEATURES__ = "features"
FLOAT_ = "float"
FLOAT32_ = "float64"
FLOAT64_ = "float32"
FOREST__ = "forest"
GAUSSIAN_ = "gaussian"
GBM__ = "gbm"
GLM__ = "glm"
GMM__ = "gmm"
ICA__ = "ica"
INFILE__ = "infile"
INTERCEPT__ = "intercept"
KMEANS__ = "kmeans"
KPCA__ = "kpca"
LDA__ = "lda"
LOGLIK_ = "loglik"
MAHA__ = "mahalanobis"
MAX_CENTERS__ = "max_centers"
META__ = "meta"
N_, P_, K_ = "n", "p", "k"
N_CENTERS__ = "n_centers"
N_COMPONENTS__ = "n_components"
NULL_BIC_ = "null_" + BIC_
NULL_LOGLIK_ = "null_" + LOGLIK_
OUTFOLDER__ = "outfolder"
OUTLIERS__ = "outliers"
PATH_ = "path"
PCA__ = "pca"
PLOT_FONT_ = "Tahoma"
PLOT_FONT_FAMILY_ = 'sans-serif'
PLOT_STYLE_ = "seaborn-whitegrid"
PREDICT__ = "predict"
PREDICTION__ = "prediction"
PROBABILITY__ = "probability"
PVAL__ = "pvalue"
RAW_PREDICTION__ = "rawPrediction"
RED_ = "#990000"
REGRESSION__ = "regression"
RESPONSE__ = "response"
RESPONSIBILITIES__ = "responsibilities"
SPARK__ = "spark"
SPARKIP__ = SPARK__ + "ip"
SPARKPARAMS__ = SPARK__ + "params"
TOTAL_VAR_ = "total_variance"
TSV_ = "tsv"
WITHIN_VAR_ = "within_cluster_variance"

CLUSTERING_INFILE__ = CLUSTERING__ + "_" + INFILE__
DIM_RED_INFILE__ = DIM_RED__ + "_" + INFILE__
OUTLIERS_INFILE__ = OUTLIERS__ + "_" + INFILE__
PREPROCESSING_METHODS__ = [DIM_RED__]
REGRESSION_INFILE__ = REGRESSION__ + "_" + INFILE__
REQUIRED_ARGS__ = [SPARK__, INFILE__, OUTFOLDER__]
RULE_INFILE__ = "rule" + "_" + INFILE__
SAMPLE__ = "sample"
DIV_METHODS__ = [SAMPLE__]

METHODS__ = PREPROCESSING_METHODS__ + \
            [CLUSTERING__, REGRESSION__] + \
            DIV_METHODS__
PARENT_METHODS__ = collections.OrderedDict(
  [(CLUSTERING__, PREPROCESSING_METHODS__),
   (DIM_RED__, None),
   (REGRESSION__, None),
   (SAMPLE__, None)])
