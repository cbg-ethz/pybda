#!/usr/bin/env Rscript

suppressPackageStartupMessages(library(argparse))
suppressPackageStartupMessages(library(stringr))
suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(readr))
suppressPackageStartupMessages(library(tidyr))
suppressPackageStartupMessages(library(tibble))
suppressPackageStartupMessages(library(ggplot2))
suppressPackageStartupMessages(library(hrbrthemes))
suppressPackageStartupMessages(library(ggthemr))
suppressPackageStartupMessages(library(purrr))
suppressPackageStartupMessages(library(viridis))
suppressPackageStartupMessages(library(cowplot))

suppressWarnings(ggthemr("fresh", "scientific"))
suppressMessages(hrbrthemes::import_roboto_condensed())

library(futile.logger)
logr <- "logger"
flog.logger(logr, futile.logger::INFO)


.plot.explained.variance <- function(lrt.tab, dir, pre)
{
  plot.tab <- dplyr::select(lrt.tab, current_model, current_expl, percent_improvement)
  plot.tab <- rbind(plot.tab, c(lrt.tab$K_max[1], lrt.tab$K_expl[1], 0))
  pl <- ggplot(lrt.tab) +
    geom_point(aes(current_model, current_expl)) +
    geom_line(aes(current_model, current_expl)) +
    scale_x_continuous("#cluster centers") +
    scale_y_continuous("Explained variance") +
    theme_minimal() +
    hrbrthemes::theme_ipsum_rc(base_family = "Helvetica") +
    theme(panel.grid.major.x=element_blank(),
          panel.grid.minor.x=element_blank(),
          axis.text.y=element_text(size=15),
          axis.text.x=element_text(size=15),
          axis.title.y=element_text(size=20),
          axis.title.x=element_text(size=20))

  for (i in c("eps", "png", "svg"))
  {
    ggsave(filename=paste0(dir, "/", pre, "-explained-variance." , i), pl, width=15, height=10, dpi=720)
  }
}


(run <- function() {
  parser <- ArgumentParser()
  parser$add_argument(
    "-f", "--file", help = "The LRT file, e.g. 'kmeans-fit-recursive-lrt_path.tsv'"
  )

  opt <- parser$parse_args()
  if (is.null(opt$file))
  {
    parser$print_help()
    stop("", call. = FALSE)
  }

  dir <- dirname(opt$file)
  pre <- sub("-lrt_path.tsv", "", basename(opt$file))
  lg.file <- paste0(dir, "/kmeans-fit-plot.log")
  flog.appender(appender.file(lg.file), name=logr)

  lrt.tab <- read_tsv(opt$file) %>%
    dplyr::select(-left_bound, -right_bound) %>%
    unique()

  .plot.explained.variance(lrt.tab, dir, pre)
})()
