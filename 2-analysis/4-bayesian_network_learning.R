library(dplyr)
library(dtplyr)
library(tibble)
library(stringr)
library(data.table)
library(bnlearn)
library(optparse)

library(ggplot2)
library(hrbrthemes)
library(ggthemr)
library(viridis)
library(cowplot)

hrbrthemes::import_roboto_condensed()
extrafont::loadfonts()

options(stringsAsFactors=FALSE)

dir <- "/Users/simondi/PROJECTS/target_infect_x_project/results/2-analysis/2-pca/"
if (!dir.exists(dir))
{
  dir <- "/cluster/home/simondi/simondi/results"
}
file.in        <- list.files(dir, pattern="-.tsv", full.names=TRUE)
file.in.header <- list.files(dir, pattern="header.tsv", full.names=TRUE)

bn.learn <- function(algo)
{

  message(paste("Learning network with", algo, "!"))

  full.tbl <- readr::read_tsv(file.in, col_names=TRUE) %>% as_tibble
  header <-
     readr::read_tsv(file.in.header, col_names=FALSE) %>%
     dplyr::select(X1) %>% unlist %>% unname
  header <- header[
      startsWith(header, "cells") |
      startsWith(header, "nucle") |
      startsWith(header, "peri")]

  colnames(full.tbl)[startsWith(colnames(full.tbl), "Feature_")] <- header
  for (he in header)
  {
    print(he)
    full.tbl[he] <- factor(cut(full.tbl[[he]], 1000, labels=FALSE))
  }
  learn.tb <- full.tbl %>% dplyr::select(-prediction, -pc1, -pc2)
  learn.tb$pathogen <- factor(learn.tb$pathogen)
  learn.tb$gene <- factor(learn.tb$gene)
  learn.tb$sirna <- factor(learn.tb$sirna)
  learn.tb <- as.data.frame(learn.tb)

  learn.tb$nuclei.children_cells_count <- NULL
  learn.tb$perinuclei.children_cells_count <- NULL
  learn.tb$nuclei.children_perinuclei_count <- NULL

  net <- switch(
      algo,
      "gs"      = bnlearn::gs(as.data.frame(learn.tb)),
      "iamb"    = bnlearn::iamb(as.data.frame(learn.tb)),
      "mmpc"    = bnlearn::mmpc(as.data.frame(learn.tb)),
      "hc"      = bnlearn::hc(as.data.frame(learn.tb)),
      "tabu"    = bnlearn::tabu(as.data.frame(learn.tb)),
      "chowliu" = bnlearn::chow.liu(as.data.frame(learn.tb))
    )
    net <- bnlearn::gs(as.data.frame(learn.tb))

    out.net <- sub(".tsv", paste0("-", algo, "-net.rds"),  file.in)
    saveRDS(net, file=out.net)
}

run <- function()
{

  option_list <- list(
    make_option(c("-a", "--algorithm"), action="store", help="algorithm to learn BN", type="character"))
  opt_parser <- OptionParser(option_list=option_list)
  opt        <- parse_args(opt_parser)

  algos <- c("gs", "iamb", "mmpc", "hc", "tabu", "chowliu")
  if (is.null(opt$algorithm))
  {
    print_help(opt_parser)
    stop(paste("Please provide correct arguments:", paste(algos, sep="/", collapse="/")))
  }
  algo <- opt$algorithm
  if (algo %in% algos)
  {
    stop(paste("Algorithm", algo, "does not exist!"))
  }

  bn.learn(algo)
}

run()
