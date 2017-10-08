library(dplyr)
library(tibble)
library(readr)
library(ggplot2)
library(hrbrthemes)
library(ggthemr)
library(viridis)
library(cowplot)
hrbrthemes::import_roboto_condensed()

options(stringsAsFactors=FALSE)

fl <- "~/Desktop/test_ba/pca_transform-cells_sample_10_normalized_cut_100_K005_sample.tsv"
fl.plot.out <- ""


plot.maxsets <- function()
{
  tbl <- readr::read_tsv(fl, col_names=TRUE)

   a <- ggplot2::ggplot(tbl) +
    xlab("PC 1") +
    ylab("PC 2") +
    hrbrthemes::theme_ipsum_rc() +
    ggplot2::theme(axis.text.x  = ggplot2::element_text( size=18),
                   axis.text.y  = ggplot2::element_text(size=18),
                   axis.title.x   = ggplot2::element_text(size=20),
                   axis.title.y   = ggplot2::element_text(size=20),
                   panel.grid.major.x = element_line(colour = 'black', linetype = 'dotted'))

  #sirna.plt    <- a + geom_point(aes(pc1, pc2, shape=sirna, color=factor(prediction))) +
  #  scale_shape_manual(values=1:nlevels(tbl$sirna))
  pathogen.plt <- a + geom_point(aes(pc1, pc2, color=pathogen, shape=factor(prediction))) +
    scale_color_viridis(discrete=T, name="Pathogen") +
    scale_shape(name="Cluster")
  gene.plt     <- a + geom_point(aes(pc1, pc2, color=gene, shape=factor(prediction))) +
    scale_color_viridis(discrete=T, name="Gene") +
    scale_shape(name="Cluster")

  cow <- cowplot::plot_grid(pathogen.plt, gene.plt, nrow=1)
  ggsave(plot=cow, file.plot.out, width=11)
}

plot.singlecells()
