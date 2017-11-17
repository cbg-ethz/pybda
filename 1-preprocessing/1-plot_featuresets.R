#!/usr/bin/env Rscript

library(dplyr)
library(dtplyr)
library(tibble)
library(data.table)
library(stringr)
library(reshape2)
library(ggplot2)
library(hrbrthemes)
library(ggthemr)

ggthemr("fresh", "scientific")
hrbrthemes::import_roboto_condensed()

options(stringsAsFactors=FALSE)

dir <- "/Users/simondi/PROJECTS/target_infect_x_project/"
file.features <- paste(dir, "results/1-preprocessing/0-features/current_analysis/featuresets_feature_files.tsv", sep="/")
file.maxsets  <- paste(dir, "results/1-preprocessing/0-features/current_analysis/feature_sets_max.tsv", sep="/")

file.overlap.plot   <- paste(dir, "results/1-preprocessing/0-features/current_analysis/feature_overlap.eps", sep="/")
file.histogram.plot <- paste(dir, "results/1-preprocessing/0-features/current_analysis/feature_histogram.eps", sep="/")
file.overlaps       <- paste(dir, "results/1-preprocessing/0-features/current_analysis/feature_overlap.tsv", sep="/")


plot.heatmap <- function()
{
  conn <- file(file.features, open="r")
  linn <- readLines(conn)
  els <- list()
  for (i in 1:length(linn))
  {
    spl      <- stringr::str_split(linn[i], "\t")
    pref     <- paste(stringr::str_split(spl[[1]][1], "-")[[1]][-1], collapse="-")
    features <- spl[[1]][2]
    features <- tolower(stringr::str_split(features, ",")[[1]])
    features <- grep("^cells|^nuclei|^perinucl", features, value=T)
    els[[pref]] <- features
  }

  close(conn)
  len.els <- length(els)
  overlap.matrix <- matrix(0, len.els, len.els)

  jaccard <- function(a, b)
  {
    nom <- length(intersect(a, b))
    den <- length(union(a, b))
    den <- ifelse(den == 0 & nom == 0, 1, den)

    nom / den
  }

  colnames(overlap.matrix) <- rownames(overlap.matrix) <- names(els)
  for (i in seq(len.els))
  {
    for (j in seq(len.els))
    {
      overlap.matrix[i, j] <- jaccard(els[[i]], els[[j]])
    }
  }

  overlap.frame <- reshape2::melt(overlap.matrix) %>% as.tbl %>%
    dplyr::mutate(Var1 = as.character(Var1),
                  Var2 = as.character(Var2)) %>%
    dplyr::arrange(Var1, Var2)

  ggplot2::ggplot(overlap.frame,  ggplot2::aes(Var1, Var2)) +
    ggplot2::geom_tile(aes(fill=value), colour="black") +
    ggplot2::scale_x_discrete(expand = c(0,0)) +
    ggplot2::scale_y_discrete(expand = c(0,0),
                              name="",
                              limits=rev(levels(factor(overlap.frame$Var2)))) +
    hrbrthemes::theme_ipsum_rc() +
    ggplot2::theme(
                   axis.text.x  = ggplot2::element_blank(),
                   axis.text.y  = ggplot2::element_text(size=11),
                   axis.title   = ggplot2::element_blank(),
                   axis.ticks   = ggplot2::element_blank(),
                   legend.title = element_text(size=15),
                   legend.text  = element_text(size=15)) +
    guides(fill = guide_legend("Jaccard"))

  ggsave(file.overlap.plot, width=11, height=10)
}

plot.maxsets <- function()
{
  conn <- file(file.maxsets, open="r")
  linn <- readLines(conn)
  close(conn)

  els <- list()
  for (i in 1:length(linn))
  {
    if (i == 1) next
    spl          <- stringr::str_split(linn[i], "\t")
    feature.size <- spl[[1]][1]
    screen.size  <- spl[[1]][4]
    els[[screen.size]] <- feature.size
  }

  set.frame <- data.frame("screens"  = names(els),
                          "features" = as.integer(unname(unlist(els))))

  set.frame$screens <- factor(set.frame$screens, levels=rev(set.frame$screens))

  ggplot2::ggplot(set.frame) +
    geom_bar(aes(screens, features), stat="identity") +
    ggplot2::scale_x_discrete(expand = c(0,0),
                              breaks = c(1, seq(5, 50, by=5), max(as.integer(set.frame$screens)))) +
    guides(fill = guide_legend("Jaccard")) +
    xlab("#screens") +
    ylab("#features of intersect") +
    hrbrthemes::theme_ipsum_rc() +
    ggplot2::theme(axis.text.x  = ggplot2::element_text(size=18),
                   axis.text.y  = ggplot2::element_text(size=18),
                   axis.title.x   = ggplot2::element_text(size=20),
                   axis.title.y   = ggplot2::element_text(size=20),
                   panel.grid.major.x = element_line(colour = 'black', linetype = 'dotted'))

  ggsave(file.histogram.plot, width=11, height=10)
}

plot.heatmap()
plot.maxsets()
