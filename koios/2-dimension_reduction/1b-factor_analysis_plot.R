#!/usr/bin/env Rscript

suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(ggplot2))
suppressPackageStartupMessages(library(hrbrthemes))
suppressPackageStartupMessages(library(ggthemr))
suppressPackageStartupMessages(library(viridis))
suppressPackageStartupMessages(library(argparse))
suppressPackageStartupMessages(library(cowplot))
suppressPackageStartupMessages(library(ggrepel))
suppressPackageStartupMessages(library(argparse))

theme <- ggthemr("fresh", "scientific")
suppressMessages(hrbrthemes::import_roboto_condensed())
options(stringsAsFactors=FALSE)


plot.likelihood <- function(plotout, likelhood.file)
{
  full.tbl <- readr::read_tsv(likelhood.file, col_names=FALSE) %>%
    as.tbl %>%
    dplyr::mutate(Iteration=0:(n()-1)) %>%
    as.data.frame()

  lims <- c(4.8e08, 6.9e08, 8.9e08, 1.1e09, 1.3e09)
  plt <-
    ggplot2::ggplot(full.tbl, aes(x=Iteration, y=X1)) +
    ggplot2::geom_line(size=1.25) +
    xlab("Iteration") +
    ylab(expression(paste("-\u2113(", theta, ")"))) +
    hrbrthemes::theme_ipsum() +
    scale_y_reverse(labels=rev(lims), breaks= lims) +
    ggplot2::theme(axis.text.x  = ggplot2::element_text( size=18),
                   axis.text.y  = ggplot2::element_text(size=18),
                   axis.line = element_line(size = .5, linetype = "solid"),
                   panel.grid.minor = element_blank(),
                   panel.grid.major = element_blank(),
                   axis.title.x   = ggplot2::element_text(size=20),
                   axis.title.y   = ggplot2::element_text(size=20))

  for (i in c("png", "svg")) {
    ggsave(plot=plt, filename=paste0(plotout, ".", i), dpi=720, width=10, height=7)
  }

}


