#!/usr/bin/env Rscript

suppressPackageStartupMessages(library(argparse))
suppressPackageStartupMessages(library(stringr))
suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(tibble))
suppressPackageStartupMessages(library(readr))
suppressPackageStartupMessages(library(tidyr))
suppressPackageStartupMessages(library(ggplot2))
suppressPackageStartupMessages(library(hrbrthemes))
suppressPackageStartupMessages(library(ggthemes))
suppressPackageStartupMessages(library(ggthemr))
suppressPackageStartupMessages(library(purrr))
suppressPackageStartupMessages(library(colorspace))
suppressPackageStartupMessages(library(cowplot))
suppressMessages(hrbrthemes::import_roboto_condensed())


library(futile.logger)
logr <- "logger"
flog.logger(logr, futile.logger::INFO)


find.interesting.clusters <- function(cc.file)
{
  cell.counts <- readr::read_csv(cc.file, col_names = c("X1", "LineCount", "File")) %>%
    dplyr::mutate(CellCount = LineCount - 1) %>%
    dplyr::select(CellCount, File) %>%
    dplyr::arrange(CellCount)

  which(cell.counts$CellCount == quantile(cell.counts$CellCount, .5))

  cell.counts <- cell.counts[c(
    seq(5),
    (nrow(cell.counts) - 5):nrow(cell.counts),
    which(cell.counts$CellCount == quantile(cell.counts$CellCount, .5))),
  ]

  cell.counts$File
}


(run <- function() {
  parser <- ArgumentParser()
  parser$add_argument(
    "-f", "--folder", help = paste("tsv file that contains clustering, e.g. kmeans-transformed-recursive-clusters"),
    "-c", "--cel0counts", help = paste("cell count file, e.g. 'kmeans-transformed-recursive-clusters-cell_counts.tsv'")
  )

  opt <- parser$parse_args()
  if (is.null(opt$folder) || is.null(opt$silhouettes))
  {
    stop(parser$print_help())
  }

  data.dir <- "/Users/simondi/PROJECTS/target_infect_x_project/results/2-analysis/2-clustering/current/kmeans-transformed-recursive-clusters"
  cc.file <- "/Users/simondi/PROJECTS/target_infect_x_project/results/2-analysis/2-clustering/current/kmeans-transformed-recursive-clusters-cell_counts.tsv"

  data.dir <- opt$folder
  lg.file  <- paste0(data.dir, "/kmeans-transformed-cluster_analysis.log")
  flog.appender(appender.file(lg.file), name=logr)

  good.clusters <- find.interesting.clusters(cc.file)
  purrr:::map_dfr(good.clusters, function(.) {
    cluster.idx <- stringr::str_match(good.clusters[1], pattern="cluster_(.*).tsv")[1]
    df <- read_tsv(.)
    cbind(Cluster = cluster.idx, df)
  }


})()
