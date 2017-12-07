library(dplyr)
library(dtplyr)
library(data.table)
library(tibble)
library(ggplot2)
library(hrbrthemes)
library(ggthemr)
library(viridis)
library(cowplot)

ggthemr("fresh", "scientific")

hrbrthemes::import_roboto_condensed()
extrafont::loadfonts()

dir <- "/Users/simondi/PROJECTS/target_infect_x_project/results/2-analysis/2-clustering/current/"
bic.file         <- list.files(dir, pattern="BIC.*.tsv", full.names=TRUE)
gene.pred.folder <- list.files(dir, pattern="gene_pathogen_prediction_count", full.names=TRUE)

plot.bic <- function(bic.file)
{
  fl <- readr::read_tsv(bic.file, col_names=TRUE)
  plt <- ggplot(fl, aes(x=index, y=stat)) +
    geom_line(lwd=1, color="black") +
    geom_point(size=3) +
    geom_label(data=subset(fl,index>=5000) , aes(x=index, y=stat, label=floor(stat)), size=5,  fontface = "bold", vjust=-.5) +
    hrbrthemes::theme_ipsum_rc() +
    scale_y_log10(breaks=scales::pretty_breaks(n=4)) +
    ylab("BIC") + xlab("Cluster centers") +
    ggplot2::theme(axis.text.x  = ggplot2::element_text( size=18),
                   axis.text.y  = ggplot2::element_text(size=18),
                   axis.title.x   = ggplot2::element_text(size=20),
                   axis.title.y   = ggplot2::element_text(size=20),
                   panel.grid.major.x = element_line(colour = 'black', linetype = 'dotted'))
  ggsave(filename=sub(".tsv", ".eps", bic.file), plt)
  ggsave(filename=sub(".tsv", ".png", bic.file),plt, dpi=1080)

}

plot.bic(bic.file)
