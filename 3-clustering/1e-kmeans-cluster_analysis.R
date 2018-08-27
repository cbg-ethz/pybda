#!/usr/bin/env Rscript

suppressPackageStartupMessages(library(argparse))
suppressPackageStartupMessages(library(stringr))
suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(tibble))
suppressPackageStartupMessages(library(readr))
suppressPackageStartupMessages(library(tidyr))
suppressPackageStartupMessages(library(ggplot2))
suppressPackageStartupMessages(library(here))
suppressPackageStartupMessages(library(hrbrthemes))
suppressPackageStartupMessages(library(ggthemes))
suppressPackageStartupMessages(library(ggthemr))
suppressPackageStartupMessages(library(purrr))
suppressPackageStartupMessages(library(colorspace))
suppressPackageStartupMessages(library(cowplot))
suppressPackageStartupMessages(library(here))
suppressMessages(hrbrthemes::import_roboto_condensed())


.path <- here("3-clustering/")
source(paste0(.path, "_ora.R"))
source(paste0(.path, "_util.R"))


library(futile.logger)
logr <- "logger"
flog.logger(logr, futile.logger::INFO)


my.theme <- function(title.hjust = 0, legend_pos="bottom") {
  theme(
    axis.text = element_text(size = 8),
    axis.title.x = element_text(size = 8, face = "bold",
                                hjust = 1),
    axis.title.y = element_text(size = 8, face = "bold"),
    plot.title = element_text(size = 8, face = "bold",
                              hjust = title.hjust),
    plot.margin = rep(grid::unit(1, "cm"), 4),
    strip.text.x = element_text(size = 8),
    strip.text.y = element_text(size = 8),
    axis.line = element_blank(),
    legend.position = legend_pos) +
    background_grid(
      major = "y", minor = "y",
      colour.major = "grey80", colour.minor = "grey90",
      size.major = 0.2, size.minor = 0.2
    )
}


.find.interesting.clusters <- function(cc.file)
{
  cell.counts <- readr::read_csv(cc.file, col_names = c("X1", "LineCount", "File")) %>%
    dplyr::mutate(CellCount = LineCount - 1) %>%
    dplyr::select(CellCount, File) %>%
    dplyr::arrange(CellCount) %>%
    dplyr::group_by(File) %>%
    dplyr::mutate(Cluster =  stringr::str_match(File, pattern="cluster_(\\d+).tsv")[2]) %>%
    ungroup()

  which(cell.counts$CellCount == quantile(cell.counts$CellCount, .5))

  cell.counts <- cell.counts[c(
    seq(5),
    (nrow(cell.counts) - 5):nrow(cell.counts),
    which(cell.counts$CellCount == quantile(cell.counts$CellCount, .5))),
  ]

  cell.counts
}


.get.two.clusters <- function(good.clusters, clusters)
{
  two.clusters <- good.clusters %>%
    dplyr::mutate(Order = order(good.clusters$CellCount)) %>%
    dplyr::filter(CellCount == max(CellCount) |
                  CellCount == min(CellCount)) %>%
    dplyr::group_by(File) %>%
    dplyr::mutate(Cluster =  stringr::str_match(File, pattern="cluster_(\\d+).tsv")[2]) %>%
    ungroup()

  two.clusters
}


.ora <- function(good.clusters, clusters, universe, data.dir)
{
  two.clusters.idx <- .get.two.clusters(good.clusters, clusters)
  two.clusters <- dplyr::filter(clusters, prediction %in% two.clusters.idx$Cluster)

  oras <- list()
  for (i in two.clusters$Cluster)
  {
    cluster.genes <- dplyr::filter(clusters, prediction==i) %>%
      dplyr::pull(gene) %>%
      unique()
    oras[[paste(i)]] <- ora(cluster.genes, universe)
  }

  oras.flat <- map_dfr(
    seq(oras),
    function(i)
    {
      cbind(Cluster=names(oras)[i],  oras[[i]]$summary) %>%
        as.tibble() %>%
        dplyr::filter(!is.na(Pvalue))
    })

  two.cluster.ora <- oras.flat %>% filter(Qvalue < .05)
  two.cluster.ora$Size <- "Big"
  two.cluster.ora$Size[two.cluster.ora$Cluster == 3652] <- "Small"
  saveRDS(two.cluster.ora, paste0(data.dir, "/two_cluster_ora.rds"))
  readr::write_tsv(two.cluster.ora, paste0(data.dir, "/two_cluster_ora.tsv"))

  some.cells <- filter(two.clusters,
         pathogen=="bartonella",
         gene!="none",
         gene!="unknown",
         sirna!="none",
         library=="d",
         design=="p") %>%
    group_by(Cluster) %>% top_n(10, row_number())

}


.plot.factors <- function(clusters, good.clusters, data.dir)
{
  good.cluster.idx <- good.clusters %>%
    dplyr::pull(Cluster) %>%
    unique()

  cnt <- 5
  plot.clusters <- good.clusters %>%
    dplyr::arrange(CellCount)  %>%
    .[c(seq(cnt), seq(nrow(.) - cnt  + 1, nrow(.))),] %>%
    dplyr::mutate(Size = rep(c("Small", "Big"), each=nrow(.)/2)) %>%
    dplyr::select(Cluster, Size) %>%
    dplyr::mutate(Cluster = as.integer(Cluster))

  two.clusters.idx <- .get.two.clusters(good.clusters, clusters)
  two.clusters <- dplyr::filter(clusters, prediction %in% two.clusters.idx$Cluster)

  factors <- dplyr::filter(clusters, Cluster %in% plot.clusters$Cluster) %>%
    dplyr::left_join(plot.clusters, by="Cluster") %>%
   dplyr::filter(Cluster %in% c(3652, 13295, 3654, 13315, 3579, 9902))

  p <- ggplot2::ggplot(data=factors) +
    geom_point(aes(f_0, f_1, color = as.factor(Cluster), shape=as.factor(Size)), size = 1.75, alpha=.6) +
    scale_x_continuous("Factor 1", labels=0:1, breaks=0:1) +
    scale_y_continuous("Factor 2") +
    scale_shape_discrete("Cluster size") +
    scale_color_manual(
      values = colorspace::desaturate(amount=.5, viridis::viridis(6, end=.85))
    ) +
    guides(color=FALSE, shape=guide_legend(override.aes = list(size = 5))) +
    hrbrthemes::theme_ipsum_rc("Helvetica") +
    my.theme()  +
    theme(panel.grid.major=element_blank(),
          axis.text.x=element_text(size=12),
          axis.text.y=element_text(size=12),
          panel.grid.minor = element_blank(),
          legend.title=element_text(size=18),
          legend.text=element_text(size=16),
          plot.title=element_text(size=22),
          axis.title.y=element_text(size=16),
          axis.title.x=element_text(size=16)) +
    ggthemes::geom_rangeframe(aes(f_0, f_1)) +
    labs(title = "")

  p

  for (i in c("pdf", "svg", "png")) {
    cowplot::ggsave2(paste0(data.dir, "/plot-factors-extreme_clusters.", i), p, width=10, height=6, dpi=720)
  }

}


(run <- function() {
  parser <- ArgumentParser()
  parser$add_argument(
    "-f", "--folder", help = paste("folder that contains all output")
  )

  opt <- parser$parse_args()
  if (is.null(opt$folder) || is.null(opt$silhouettes))
  {
    stop(parser$print_help())
  }

  data.dir        <- "/Users/simondi/PROJECTS/target_infect_x_project/results/2-analysis/2-clustering/current"
  gene.pred.fold  <- list.files(data.dir, pattern="gene_prediction_counts$", full.names=T)
  #clusters.dir    <- paste0(data.dir,  "/kmeans-transformed-recursive-clusters")
  cc.file <- "/Users/simondi/PROJECTS/target_infect_x_project/results/2-analysis/2-clustering/current/kmeans-transformed-recursive-clusters-cell_counts.tsv"


  lg.file  <- paste0(data.dir, "/kmeans-transformed-cluster_analysis.log")
  flog.appender(appender.file(lg.file), name=logr)

  universe <- read.gene.predictions(gene.pred.fold) %>%
    dplyr::pull(gene) %>%
    unique()
  good.clusters <- .find.interesting.clusters(cc.file)

  clusters <- purrr:::map_dfr(good.clusters$File, function(.) {
    cluster.idx <- as.integer(stringr::str_match(., pattern="cluster_(.*).tsv")[2])
    df <- read_tsv(.)
    add_column(Cluster = cluster.idx, df, .before=TRUE)
  })

  .ora(good.clusters, clusters, universe, data.dir)
  .plot.factors(clusters, good.clusters, data.dir)
})()
