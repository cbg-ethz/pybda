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

  for (col in cols)
  {
    cl <- fr[ ,get(col)]
    cl.var  <- var(cl, na.rm=T)
    cl.mean <- mean(cl, na.rm=TRUE)
    cl.no.out <- which(abs(fr[ ,get(col)]) <= cl.mean + 4 * cl.var)

    pl <- ggplot(fr[cl.no.out], aes(x=fr[cl.no.out ,get(col)])) +
      hrbrthemes::theme_ipsum_rc(base_family="Helvetica") +
      scale_x_continuous(paste(col)) +
      scale_y_continuous("Count") +
      geom_histogram(bins=100, fill="darkgrey") +
      theme(panel.grid.major=element_blank(),
            axis.title.y = element_text(size=20),
            axis.title.x = element_text(size=20),
            axis.text.x = element_text(size=15),
            axis.text.y = element_text(size=15),
            panel.grid.minor = element_blank(),
            axis.line = element_line(color="black", size = .75))

    fl.o <- tolower(sub(" ", "_" , col))
    for (form in c("eps", "png", "svg"))
    {
        ggsave(plot=pl, paste0(out.dir ,"/feature_", fl.o, ".", form),
               dpi=720, width=8, height=10)
    }
  }

}

(run <- function()
{
  parser <- ArgumentParser()
  parser$add_argument("infile", help = "Name of subsampled fa entries (e.g. 'fa-sample.tsv')", type="character")
  opt <- parser$parse_args()
  fl <- opt$infile
  dir <- stringr:::str_match("(.*).tsv", string=fl)[2]
  out.dir   <- paste0(dir, "-feature_distributions/")

  plot.distributions(out.dir, fl)
})()
