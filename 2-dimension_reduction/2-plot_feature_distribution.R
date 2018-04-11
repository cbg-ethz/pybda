#!/usr/bin/env Rscript

library(dplyr)
library(dtplyr)
library(data.table)
library(stringr)
library(tidyr)
library(ggplot2)
library(hrbrthemes)
library(ggthemr)
library(rutil)

hrbrthemes::import_roboto_condensed()

options(stringsAsFactors=FALSE)

data.dir  <- "/Users/simondi/PHD/data/data/target_infect_x/query_data/"
out.dir   <- "/Users/simondi/PROJECTS/target_infect_x_project/results/1-preprocessing/0-features/current_analysis/feature_distributions/"
data.file <- paste(data.dir, "all_optimal_from_file_feature_dbq_250_cells_10.tsv", sep="/")


plot.distributions <- function()
{
  fr           <- fread(data.file, sep="\t")
  cols         <- colnames(fr)
  feature.idxs <- which(stringr::str_detect(cols, "cells|nuclei|peri"))
  if (!dir.exists(out.dir)) dir.create(out.dir)

  for (col in cols[feature.idxs]) {
    cl <- fr[ ,get(col)]
    cl.var  <- var(cl, na.rm=T)
    cl.mean <- mean(cl, na.rm=TRUE)
    cl.no.out <- which(abs(fr[ ,get(col)]) <= cl.mean + 4 * cl.var)

    pl <- ggplot(fr[cl.no.out], aes(x=fr[cl.no.out ,get(col)])) +
      hrbrthemes::theme_ipsum_rc(base_family="Helvetica") +
      scale_x_continuous(paste("Feature:", col)) +
      scale_y_continuous("Count") +
      geom_histogram(bins=100, fill="darkgrey") +
      theme(panel.grid.major=element_blank(),
            axis.title.y = element_text(size=12),
            axis.title.x = element_text(size=12))
    rutil::saveplot(pl, paste0("feature_", col), out.folders=out.dir, format=c("eps", "png", "svg"))
  }
}

plot.distributions()
