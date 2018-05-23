#!/usr/bin/env Rscript

suppressPackageStartupMessages(library(argparse))
suppressPackageStartupMessages(library(stringr))
suppressPackageStartupMessages(library(readr))
suppressPackageStartupMessages(library(ggplot2))
suppressPackageStartupMessages(library(colorspace))
suppressPackageStartupMessages(library(hrbrthemes))
suppressPackageStartupMessages(library(ggthemr))
suppressPackageStartupMessages(library(purrr))
suppressPackageStartupMessages(library(futile.logger))
suppressPackageStartupMessages(library(ggridges))

suppressMessages(hrbrthemes::import_roboto_condensed())

logr <- "logger"
flog.logger(logr, futile.logger::INFO)

plot.cluster.sizes <- function(plot.folder)
{
  plot.folder <- ""
  pls <- list.files(plot.folder,  pattern="cluster_?[s|S]izes.tsv", full.names=TRUE)
  dat <- purrr::map_dfr(pls, function(e) {
    # parse the number of clusters from the file name
    fl.suf <- as.integer(str_match(string=e, pattern=".*K(\\d+).*tsv")[2])
    tab    <- readr::read_tsv(e, col_names="K", col_types="i")
    tab$ClusterCount <- fl.suf
    tab
  })

  ggplot(dat, aes(x = dat$K, y = factor(dat$ClusterCount), fill=factor(dat$ClusterCount))) +
    geom_density_ridges(stat = "binline", scale = .4, draw_baseline = FALSE, bins=100, alpha=.5,
    ) +
    theme_ridges() +
    hrbrthemes::theme_ipsum() +
    colorspace::scale_fill_discrete_sequential("Blues", c1 = 20, c2 = 70, l1 = 25, l2 = 100) +
    scale_y_discrete("# clusters") +
    scale_x_log10("# cells per cluster") +
    guides(fill=FALSE)

}


(run <- function()
{
  parser <- ArgumentParser()
  parser$add_argument("-f", "--folder", help = "folder where the cluster size files lie")

  opt <- parser$parse_args()
  if (is.null(opt$folder))
  {
    stop(parser$print_help())
  }

  lg.file <- paste0(dir, "/kmeans-fit-plot.log")
  flog.appender(appender.file(lg.file), name=logr)

  plot.cluster.sizes(opt$folder)
})()
