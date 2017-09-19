library(dplyr)
library(tidyr)
library(tibble)
library(data.table)
library(stringr)
library(reshape2)
library(ggplot2)
library(ggsci)
library(hrbrthemes)
hrbrthemes::import_roboto_condensed()

options(stringsAsFactors=FALSE)

dir <- "/Users/simondi/PROJECTS/target_infect_x_project/"
file.overlap.plot     <- paste(dir, "plots/mock_normalisation_plot", sep="/")
mock.unnormalized <- paste(dir, "data/target_infect_x/query_data/sample_10_mock.tsv", sep="/")
mock.normalized <- paste(dir, "data/target_infect_x/query_data/sample_10_mock_normalize.tsv", sep="/")


plot.densities <- function()
{

  unnorm.frame <-  data.table::fread(mock.unnormalized, sep="\t", header=TRUE)
  norm.frame <-  data.table::fread(mock.normalized, sep="\t", header=TRUE)
  cols <- gsub("\\.", "_", colnames(unnorm.frame))
  colnames(unnorm.frame) <- colnames(norm.frame) <- cols
  feature.col.idxs <- sapply(cols, function(e) {
    startsWith(e, "cells") || startsWith(e, "pericnu") || startsWith(e, "nuclei")
  })

  feature.cols <- cols[feature.col.idxs]
  unnorm.frame$Normalized <- "Unnormalized"
  norm.frame$Normalized <- "Normalized"
  frame <- rbindlist(list(unnorm.frame, norm.frame))
  colors <- viridisLite::magma(57)

  g <- ggplot(frame) +
    facet_grid(Normalized ~ ., scales="free") +
    ylab("Density") +
    xlab("Feature range") +
    hrbrthemes::theme_ipsum_rc()
  for (i in seq(feature.cols))
  {
    new.g <- g +
      geom_density(data=frame, aes(frame[[ feature.cols[i] ]]), alpha=1) +
      labs(title="Feature density",
           subtitle=paste0("Comparing feature densities between normalized and unnormalized feature: ", feature.cols[i])) +
    ggsave(paste(file.overlap.plot, feature.cols[i], ".eps", sep="_"), new.g)
  }
}
