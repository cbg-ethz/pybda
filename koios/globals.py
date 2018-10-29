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


WITHIN_VAR_ = "within_cluster_variance"
TOTAL_VAR_ = "total_variance"
EXPL_VAR_ = "explained_variance"
N_, P_, K_ = "n", "p", "k"
BIC_ = "BIC"
PATH_ = "path"

PLOT_FONT_ = "Tahoma"
PLOT_FONT_FAMILY_ = 'sans-serif'
PLOT_STYLE_ = "seaborn-whitegrid"
RED_ = "#990000"

TSV_ = "tsv"
DOUBLE_ = "double"
FLOAT_ = "float"
FLOAT64_ = "float32"
FLOAT32_ = "float64"

FEATURES_ = "features"
GAUSSIAN_ = "gaussian"
BINOMIAL_ = "binomial"


SPARK__ = "spark"
SPARKIP__ = "sparkip"
SPARKPARAMS__ = "sparkparams"
INFILE__ = "infile"
OUTFOLDER__ = "outfolder"

META__ = "meta"
FEATURES__ = "features"
RESPONSE__ = "response"

DIM_RED__ = "dimension_reduction"
DIM_RED_INFILE__ = "dimension_reduction_infile"
PCA__ = "pca"
KPCA__ = "kpca"
FACTOR_ANALYSIS__ = "factor_analysis"
N_COMPONENTS__ = "m_components"

OUTLIERS__ = "outliers"
OUTLIERS_INFILE__ = "outliers_infile"

CLUSTERING__ = "clustering"
CLUSTERING_INFILE__ = "clustering_infile"
KMEANS__ = "kmeans"
GMM__ = "gmm"
MAX_CENTERS__ = "max_centers"
N_CENTERS__ = "n_centers"

REGRESSION__ = "regression"
REGRESSION_INFILE__ = "regression_infile"
GLM__ = "glm"
FAMILY__ = "family"

RULE_INFILE__ = "rule_infile"

REQUIRED_ARGS__ = [
    SPARK__,
    INFILE__,
    OUTFOLDER__
]
METHODS__ = [
    DIM_RED__,
    OUTLIERS__,
    CLUSTERING__,
    REGRESSION__
]