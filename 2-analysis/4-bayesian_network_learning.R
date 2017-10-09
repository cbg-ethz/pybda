library(dplyr)
library(dtplyr)
library(tibble)
library(stringr)
library(data.table)
library(bnlearn)

library(ggplot2)
library(hrbrthemes)
library(ggthemr)
library(viridis)
library(cowplot)

hrbrthemes::import_roboto_condensed()
extrafont::loadfonts()

options(stringsAsFactors=FALSE)

dir <- "/Users/simondi/PROJECTS/target_infect_x_project/results/2-analysis/2-pca/"
file.in <- list.files(dir, pattern="-.tsv", full.names=TRUE)
file.in.header <- list.files(dir, pattern="header.tsv", full.names=TRUE)

bn.learn <- function()
{

  full.tbl <- readr::read_tsv(file.in, col_names=TRUE) %>% as_tibble
  header <-
     readr::read_tsv(file.in.header, col_names=FALSE) %>%
     dplyr::select(X1) %>% unlist %>% unname
  header <- header[
      startsWith(header, "cells") |
      startsWith(header, "nucle") |
      startsWith(header, "peri")]

  colnames(full.tbl)[startsWith(colnames(full.tbl, "Feature_"))]

}

bn.learn()
