#!/usr/bin/env Rscript

suppressPackageStartupMessages(library(argparse))
suppressPackageStartupMessages(library(stringr))
suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(tibble))
suppressPackageStartupMessages(library(readr))
suppressPackageStartupMessages(library(tidyr))
suppressPackageStartupMessages(library(ggplot2))
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


.find.interesting.clusters <- function(cc.file)
{
  cell.counts <- readr::read_csv(cc.file, col_names = c("X1", "LineCount", "File")) %>%
    dplyr::mutate(CellCount = LineCount - 1) %>%
    dplyr::select(CellCount, File) %>%
    dplyr::arrange(CellCount)

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


.ora <- function(good.clusters, clusters, universe)
{
  two.clusters.idx <- .get.two.clusters(good.clusters, clusters)
  two.clusters <- dplyr::filter(clusters, prediction %in% two.clusters.idx$Cluster)

  oras <- list()
  for (i in two.clusters$Cluster)
  {
    cluster.genes <- dplyr::filter(clusters, prediction==i) %>%
      dplyr::pull(gene) %>%
      unique()
    oras[[paste(i)]] <- .ora(cluster.genes, universe)
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

  data.dir <- "/Users/simondi/PROJECTS/target_infect_x_project/results/2-analysis/2-clustering/current"
  gene.pred.fold  <- list.files(data.dir, pattern="gene_prediction_counts$", full.names=T)
  #clusters.dir    <- paste0(data.dir,  "/kmeans-transformed-recursive-clusters")
  cc.file <- "/Users/simondi/PROJECTS/target_infect_x_project/results/2-analysis/2-clustering/current/kmeans-transformed-recursive-clusters-cell_counts.tsv"


  lg.file  <- paste0(data.dir, "/kmeans-transformed-cluster_analysis.log")
  flog.appender(appender.file(lg.file), name=logr)

  universe <- .read.gene.predictions(gene.pred.fold) %>%
    unique(gene.preductions$gene)
  good.clusters <- .find.interesting.clusters(cc.file)

  clusters <- purrr:::map_dfr(good.clusters$File, function(.) {
    cluster.idx <- as.integer(stringr::str_match(., pattern="cluster_(.*).tsv")[2])
    df <- read_tsv(.)
    add_column(Cluster = cluster.idx, df, .before=TRUE)
  })

  .ora(good.clusters, clusters, universe)
})()
