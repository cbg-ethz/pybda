#!/usr/bin/env Rscript

suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(data.table))
suppressPackageStartupMessages(library(stringr))
suppressPackageStartupMessages(library(argparse))
suppressPackageStartupMessages(library(tidyr))
suppressPackageStartupMessages(library(ggplot2))
suppressPackageStartupMessages(library(hrbrthemes))
suppressPackageStartupMessages(library(ggthemr))


suppressMessages(hrbrthemes::import_roboto_condensed())
options(stringsAsFactors=FALSE)


plot.distributions <- function(out.dir, data.file)
{
  fr           <- data.table::fread(data.file, sep="\t")
  colnames(fr) <- paste0("Factor ", seq(ncol(fr)))
  cols         <- colnames(fr)
  if (!dir.exists(out.dir)) dir.create(out.dir)

  fr <- as.matrix(fr)
  fr.maha <- stats::mahalanobis(fr, colMeans(fr), cov(fr))
  flt <- qchisq(.95, df=ncol(fr))
  fr.flt <- fr[fr.maha  <= flt, ]

  frs <- fr.flt[seq(min(nrow(fr.flt), 10000)), ]
  frs <- as.data.table(frs)

  plt <- ggplot(frs) +
    geom_point(aes(frs[,get("Factor 1")], frs[,get("Factor 2")]), size=.5) +
    hrbrthemes::theme_ipsum_rc(base_family="Helvetica") +
    scale_x_continuous("Factor 1", limits=c(-5, 5)) +
    scale_y_continuous("Factor 2", limits=c(-5, 5)) +
    theme(axis.title.y = element_text(size=20),
          axis.title.x = element_text(size=20),
          axis.text.x = element_text(size=15),
          axis.text.y = element_text(size=15),
          panel.grid.minor = element_blank())

  for (form in c("eps", "png", "svg"))
  {
      ggsave(plot=plt, paste0(out.dir ,"/feature_scatter_plot.", form),
             dpi=720, width=8, height=10)
  }

}

(run <- function()
{
  parser <- ArgumentParser()
  parser$add_argument("infile", help = "Name of subsampled fa entries (e.g. 'fa-sample.tsv', 'outliers-sample.tsv')", type="character")
  opt <- parser$parse_args()
  fl <- opt$infile
  dir <- stringr:::str_match("(.*).tsv", string=fl)[2]
  out.dir   <- paste0(dir, "-feature_distributions/")

  plot.distributions(out.dir, fl)
})()
