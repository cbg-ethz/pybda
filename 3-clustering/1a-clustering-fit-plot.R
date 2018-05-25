#!/usr/bin/env Rscript

suppressPackageStartupMessages(library(argparse))
suppressPackageStartupMessages(library(stringr))
suppressPackageStartupMessages(library(readr))
suppressPackageStartupMessages(library(dplyr))
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


plot.cluster.sizes <- function(dat, plot.folder)
{
  flog.info('Plotting cluster sizes', name=logr)

  dat$ClusterCount <- factor(dat$ClusterCount, levels=rev(sort(unique(dat$ClusterCount))))

  plt <- ggplot(dat, aes(x = dat$K, y = dat$ClusterCount, fill = dat$ClusterCount)) +
    geom_density_ridges(stat = "binline", scale = .4, draw_baseline = FALSE, bins=100, alpha=.5) +
    theme_ridges() +
    hrbrthemes::theme_ipsum() +
    colorspace::scale_fill_discrete_sequential("Blues", c1 = 20, c2 = 70, l1 = 25, l2 = 100) +
    scale_y_discrete("# clusters") +
    scale_x_log10("# cells per cluster") +
    guides(fill=FALSE) +
    theme(axis.title.x = element_text(size=20),
          axis.title.y = element_text(size=20),
          axis.text.x = element_text(size=15),
          axis.text.y = element_text(size=15))

  for (i in c("svg", "png", "eps"))
  {
      ggsave(plt,
            filename=paste0(plot.folder,"/kmeans-fit-cluster_sizes-histogram.", i),
             width=10, height=7)
  }

}


plot.cluster.stats <- function(dat, plot.folder)
{
  flog.info('Plotting cluster statistics', name=logr)

  fl.out <- paste0(plot.folder,"/kmeans-fit-cluster_sizes-stats.tsv")
  cl <-  group_by(dat, ClusterCount) %>%
    dplyr::summarize(Quantiles = paste(sprintf("%.2f", quantile(K)/max(K)), collapse=", "))
  readr::write_tsv(x=cl,  path=fl.out)
}


(run <- function() {
  parser <- ArgumentParser()
  parser$add_argument(
    "-f", "--folder",
    help = "folder where the cluster size files lie")
  parser$add_argument(
    "-a", "--algorithm",
    help = "algorithm used for clustering")

  opt <- parser$parse_args()
  if (is.null(opt$folder) || is.null(opt$algorithm))
  {
    stop(parser$print_help())
  }

  flog.appender(appender.file(lg.file), name=logr)

  plot.folder <- opt$folder
  algo        <- opt$algorithm
  lg.file <- paste0(plot.folder, "/", algo, "-fit-plot.log")

  pls <- list.files(
    plot.folder,
    pattern=paste0(algo, ".*cluster_?[s|S]izes.tsv"),
    full.names=TRUE)

  if (length(pls) == 0) {
    flog.error('No cluster files found', name=logr)
  } else {
    flog.info('Reading cluster size data', name=logr)

    dat <- purrr::map_dfr(pls, function(e) {
      # parse the number of clusters from the file name
      fl.suf <- as.integer(str_match(string=e, pattern=".*K(\\d+).*tsv")[2])
      tab    <- readr::read_tsv(e, col_names="K", col_types="i")
      tab$ClusterCount <- fl.suf
      tab
    })

    plot.cluster.sizes(dat, plot.folder)
    plot.cluster.stats(dat, plot.folder)
  }
})()
