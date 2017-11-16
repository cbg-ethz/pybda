library(dplyr)
library(dtplyr)
library(tibble)
library(ggplot2)
library(hrbrthemes)
library(ggthemr)
library(viridis)
library(cowplot)

hrbrthemes::import_roboto_condensed()
extrafont::loadfonts()

options(stringsAsFactors=FALSE)

dir <- "/Users/simondi/PROJECTS/target_infect_x_project/results/2-analysis/2-pca/"
file.in   <- list.files(dir, pattern="-.tsv", full.names=TRUE)
file.in.var   <- list.files(dir, pattern="variance.tsv", full.names=TRUE)
plot.out  <- sub(".tsv", "-scatter_plot", file.in)

plot.single.cells <- function()
{

  full.tbl <- readr::read_tsv(file.in, col_names=TRUE) %>% as.tbl
  vars     <- readr::read_lines(file.in.var)[2] %>%
    stringr::str_split("\t") %>%
    .[[1]] %>% as.double

  gprs <- group_indices(full.tbl, gene)
  full.tbl <- full.tbl %>% dplyr::mutate(g = gprs)
  tbl <- full.tbl %>% dplyr::filter(g %in% sample(gprs, 100, replace=FALSE))
  tbl2 <- tbl %>% dplyr::group_by(pathogen, gene)  %>% sample_n(10) %>% ungroup
  tbl2$prediction <- factor(tbl2$prediction, labels=seq(unique(tbl2$prediction)))

  a <- ggplot2::ggplot(tbl2) +
    xlab(paste("Explained variance:", sprintf("%1.3f", vars[1]))) +
    ylab(paste("Explained variance:", sprintf("%1.3f", vars[2]))) +
    hrbrthemes::theme_ipsum_rc() +
    ggplot2::theme(axis.text.x  = ggplot2::element_text( size=18),
                   axis.text.y  = ggplot2::element_text(size=18),
                   axis.title.x   = ggplot2::element_text(size=20),
                   axis.title.y   = ggplot2::element_text(size=20),
                   panel.grid.major.x = element_line(colour = 'black', linetype = 'dotted'))

  cluster.plt <-
    a + geom_point(aes(pc1, pc2, color=prediction), size=1, stroke=1) +
      scale_color_viridis(discrete=T, guide=FALSE) +
      labs(title="PCA colored by cluster")
  ggsave(paste(plot.out, "clustering.eps", sep="-"))
  ggsave(paste(plot.out, "clustering.png", sep="-"), dpi=450)

  pathogen.plt <-
    a + geom_point(aes(pc1, pc2, color=pathogen, shape=prediction), size=1, stroke=1) +
    scale_color_viridis(discrete=T, name="Pathogen") +
    scale_shape_manual(name="Cluster", values=1:nlevels(tbl2$prediction)) +
    labs(title="PCA colored by pathogen")
  ggsave(paste(plot.out, "pathogen.eps", sep="-"))
  ggsave(paste(plot.out, "pathogen.png", sep="-"), dpi=450)

  gene.plt <-
    a + geom_point(aes(pc1, pc2, color=gene, shape=prediction), size=1, stroke=1) +
    viridis::scale_colour_viridis(discrete=T, guide=FALSE, option="D") +
    scale_shape_manual(name="Cluster", values=1:nlevels(tbl2$prediction)) +
    labs(title="PCA colored by gene")
   ggsave(paste(plot.out, "genes.eps", sep="-"))
   ggsave(paste(plot.out, "genes.png", sep="-"), dpi=450)
}

plot.singlecells()
