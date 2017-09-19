library(dplyr)
library(tibble)
library(data.table)
library(stringr)
library(reshape2)
library(ggplot2)
library(ggthemr)
ggthemr("fresh", "scientific")

options(stringsAsFactors=FALSE)

dir <- "/Users/simondi/PROJECTS/target_infect_x_project/"
file.overlap.plot     <- paste(dir, "plots/mock_normalisation_plot.eps", sep="/")
mock.unnormalized <- paste(dir, "data/target_infect_x/query_data/sample_10_mock.tsv", sep="/")
mock.normalized <- paste(dir, "data/target_infect_x/query_data/sample_10_mock_normalize.tsv", sep="/")



plot.densities <- function()
{

  unnorm.frame <-  data.table::fread(mock.unnormalized, sep="\t", header=TRUE)
  norm.frame <-  data.table::fread(mock.normalized, sep="\t", header=TRUE)
  cols <- gsub("\\.", "_", colnames(unnorm.frame))
  colnames(unnorm.frame) <- colnames(norm.frame) <- cols
  feature.cols <- sapply(cols, function(e) {
    startsWith(e, "cells") || startsWith(e, "pericnu") || startsWith(e, "nuclei")
  })

  feature.cols <- cols[feature.cols]
  unnorm.frame$Normalized <- "Unnormalized"
  norm.frame$Normalized <- "Normalized"
  frame <- rbindlist(list(unnorm.frame, norm.frame))

  g <- ggplot(frame) +
    facet_grid(Normalized ~ ., scales="free") +
    geom_histogram(aes(frame$perinuclei_parent_expandednuclei, ..density..), bins=150)
  g

  for (col in feature.cols)
  {
    g <- g + geom_density(data=frame, aes(frame[[col]]))
  }
  g

}
