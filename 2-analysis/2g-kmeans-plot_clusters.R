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

dir <- "/Users/simondi/PROJECTS/target_infect_x_project/results/2-analysis/2-clustering/current/"

sampled.genes.file   <- list.files(dir, pattern="sampled", full.names=TRUE)
file.in.var   <- list.files(dir, pattern="variance.tsv", full.names=TRUE)

best.clusters.file  <- list.files(dir, pattern="best_clusters", full.names=TRUE)
cluster.files       <-list.files(paste(dir, "clusters", sep="/"), full.names=TRUE)

plot.best.clusters <- function()
{
  best.clusters <- readr::read_tsv(best.clusters.file, col_names=TRUE) %>% as.tbl

  fls <- lapply(best.clusters$prediction, function(i)
  {
    idx <- grep(paste0(dir, "/clusters/.*_", i, ".*tsv"), cluster.files)
    cluster.files[idx]
  }) %>% unlist

  dat <- rbindlist(lapply(fls, function(f) readr::read_tsv(f, col_names=TRUE))) %>%
    as_tibble %>%
    tidyr::separate(features, into=paste0("Factor", 1:15), sep=",") %>%
    dplyr::mutate(Factor1:=as.double(Factor1),
                  Factor2:=as.double(Factor2),
                  prediction=as.factor(prediction))

  plt <-
    ggplot(dat) +
    geom_point(aes(x=Factor1, y=Factor2, color = prediction, shape=prediction), size=.75) +
    hrbrthemes::theme_ipsum_rc() +
    ggplot2::theme(axis.text.x  = ggplot2::element_text( size=18),
                   axis.text.y  = ggplot2::element_text(size=18),
                   axis.title.x   = ggplot2::element_text(size=20),
                   axis.title.y   = ggplot2::element_text(size=20)) +
    viridis::scale_colour_viridis(discrete=T, guide=FALSE, option="D") +
    guides(shape=FALSE)

  plot.out  <- sub(".tsv", "", best.clusters.file)
  ggsave(paste(plot.out, "genes.eps", sep="-"), plot=plt)
  ggsave(paste(plot.out, "genes.png", sep="-"), dpi=1080)
}

plot.sampled.genes <- function(sampled.genes.file)
{

  full.tbl <- readr::read_tsv(sampled.genes.file, col_names=TRUE) %>% as.tbl %>%
    tidyr::separate(features, into=paste0("Factor", 1:15), sep=",") %>%
    dplyr::mutate(Factor1:=as.double(Factor1),
                  Factor2:=as.double(Factor2),
                  prediction=as.factor(prediction))

  plt <- ggplot(full.tbl) +
    geom_point(aes(x=Factor1, y=Factor2, color = gene)) +
    hrbrthemes::theme_ipsum_rc() +
    ggplot2::theme(axis.text.x  = ggplot2::element_text( size=18),
                   axis.text.y  = ggplot2::element_text(size=18),
                   axis.title.x   = ggplot2::element_text(size=20),
                   axis.title.y   = ggplot2::element_text(size=20)) +
    viridis::scale_colour_viridis(discrete=T, guide=FALSE, option="D")

  plot.out  <- sub(".tsv", "-scatter_plot", sampled.genes.file)
  ggsave(paste(plot.out, "genes.eps", sep="-"), plot=plt)
  ggsave(paste(plot.out, "genes.png", sep="-"), dpi=450)
}

#plot.sampled.genes()
