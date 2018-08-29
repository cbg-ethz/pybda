#!/usr/bin/env Rscript


suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(data.table))
suppressPackageStartupMessages(library(stringr))
suppressPackageStartupMessages(library(argparse))
suppressPackageStartupMessages(library(tidyr))
suppressPackageStartupMessages(library(ggplot2))
suppressPackageStartupMessages(library(hrbrthemes))
suppressPackageStartupMessages(library(colorspace))


suppressMessages(hrbrthemes::import_roboto_condensed())
options(stringsAsFactors=FALSE)


plot.distributions <- function(out.dir, fr, cols)
{
  for (col in cols)
  {
    cl <- fr[ ,get(col)]
    cl.var  <- var(cl, na.rm=T)
    cl.mean <- mean(cl, na.rm=TRUE)
    cl.no.out <- which(abs(fr[ ,get(col)]) <= cl.mean + 10 * cl.var)

    pl <-
      ggplot(fr[cl.no.out], aes(x=fr[cl.no.out ,get(col)])) +
      hrbrthemes::theme_ipsum_rc(base_family="Helvetica") +
      scale_x_continuous(paste(col)) +
      scale_y_continuous("Density") +
      geom_histogram(aes(y=..density..), bins=100, fill="darkgrey") +
      theme(panel.grid.major=element_blank(),
            axis.title.y = element_text(size=20),
            axis.title.x = element_text(size=20),
            axis.text.x = element_text(size=15),
            axis.text.y = element_text(size=15),
            panel.grid.minor = element_blank(),
            axis.line = element_line(color="black", size = .5))

    fl.o <- tolower(sub(" ", "_" , col))
    for (form in c("eps", "png", "svg"))
    {
        ggsave(plot=pl, paste0(out.dir ,"/feature_", fl.o, ".", form),
               dpi=720, width=8, height=10)
    }
  }
}


scatter.distributions <- function(out.dir, fr)
{
  frm <- as.matrix(fr [,1:2])
  fr$Outlier <- "TRUE"
  fr.maha <- stats::mahalanobis(frm, colMeans(frm), cov(frm))
  flt <- qchisq(.95, df=ncol(frm))
  fr$Outlier[fr.maha  <= flt] <- "FALSE"

  frs <- fr[seq(min(nrow(fr), 10000)), ]
  plt <-
    ggplot(frs) +
    geom_point(aes(frs[,get("Factor 1")], frs[,get("Factor 2")], color=Outlier), size=.5) +
    hrbrthemes::theme_ipsum() +
    scale_color_manual(values=c("FALSE"="darkgrey", "TRUE"= "#E84646"), guide=FALSE) +
    scale_x_continuous("Factor 1", limits=c(-5, 5)) +
    scale_y_continuous("Factor 2", limits=c(-5, 5)) +
    theme(axis.title.y = element_text(size=20),
          axis.title.x = element_text(size=20),
          panel.grid.major = element_blank(),
          axis.text.x = element_text(size=15),
          axis.text.y = element_text(size=15),
          axis.line = element_line(color="black", size = .5),
          panel.grid.minor = element_blank(),
          legend.position="bottom")

  for (form in c("eps", "png", "svg"))
  {
      ggsave(plot=plt, paste0(out.dir ,"/feature_scatter_plot.", form),
             dpi=720, width=10, height=6)
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

  fr           <- data.table::fread(fl, sep="\t")
  colnames(fr) <- paste0("Factor ", seq(ncol(fr)))
  cols         <- colnames(fr)
  if (!dir.exists(out.dir)) dir.create(out.dir)

  plot.distributions(out.dir, fr, cols)
  scatter.distributions(out.dir, fr)
})()
