#!/usr/bin/env Rscript

suppressPackageStartupMessages(library(argparse))
suppressPackageStartupMessages(library(stringr))
suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(tibble))
suppressPackageStartupMessages(library(readr))
suppressPackageStartupMessages(library(tidyr))
suppressPackageStartupMessages(library(ggplot2))
suppressPackageStartupMessages(library(colorspace))
suppressPackageStartupMessages(library(hrbrthemes))
suppressPackageStartupMessages(library(ggthemes))
suppressPackageStartupMessages(library(purrr))
suppressPackageStartupMessages(library(viridis))
suppressPackageStartupMessages(library(cowplot))
suppressPackageStartupMessages(library(ggridges))
suppressMessages(hrbrthemes::import_roboto_condensed())

library(futile.logger)
logr <- "logger"
flog.logger(logr, futile.logger::INFO)


my.theme <- function(title.hjust = 0, legend_pos="bottom") {
  theme(
    axis.text = element_text(size = 6,  color="grey30"),
    axis.title.x = element_text(size = 8, face = "bold",
                                hjust = 1),
    axis.title.y = element_text(size = 8, face = "bold", vjust=1),
    plot.title = element_text(size = 8, face = "bold",
                              hjust = title.hjust),
    plot.margin = rep(grid::unit(1, "cm"), 4),
    strip.text.x = element_text(size = 8),
    strip.text.y = element_text(size = 8),
    axis.line = element_blank(),
    legend.position = legend_pos,
    legend.text = element_text(size = 8),
    legend.title = element_text(size = 8)) +
    background_grid(
      minor = "y", major = "y",
      colour.major = "grey80", colour.minor = "grey90",
      size.major = 0.2, size.minor = 0.2
    )
}


plot.explained.variance <- function(data.dir, loglik.path)
{
  flog.info('Plotting explained variance', name=logr)

  sel.max <- loglik.path %>%
    dplyr::filter(current_model == max(current_model))
  sel.max$Ref <- c("Reference")
  sel.take <- loglik.path %>%
    dplyr::filter(row_number() == nrow(.))
  sel.take$Ref <- c("Selected K")

  p1 <- ggplot(data = loglik.path, aes(iteration, current_model)) +
    geom_point(size = 0.5) +
    geom_line(lwd = 0.5) +
    geom_point(data = sel.max, color = "red", size=0.5) +
    geom_point(data = sel.take, color = "red", size=0.5) +
    geom_text(data = sel.max, aes(iteration, current_model, label = Ref), hjust=-.1, size=2.5) +
    geom_text(data = sel.take, aes(iteration, current_model, label = Ref),hjust=.85, vjust=-.75, size=2.5) +
    cowplot::theme_cowplot() +
    theme(axis.ticks.x = element_blank(),
          axis.text.x = element_blank(),
          axis.ticks.y = element_line(size=.2)) +
    my.theme(-0.7) +
    scale_x_continuous(breaks = seq(0, 13, 3), limits=c(0, 13)) +
    scale_y_continuous(breaks = c(0, 19947, 25000, 50000), limits = c(-5000, 51000),
                       labels = c(0, 19947, 25000, 50000)) +
    theme(panel.grid.major.y = element_line(size=.2, colour = "white"),
          panel.grid.minor.y = element_line(size=.2, colour = "white"),
          axis.text.y = element_text(color=c("black", "red", "black", "black"))
          ) +
    geom_segment(aes(x = 1, y = -5000, xend = 13, yend = -5000),
                 arrow = arrow(length = unit(0.1, "cm"))) +
    labs(x = "# of recursions", y = "", title  = "Number of clusters")

  p2 <-  ggplot(data = loglik.path, aes(iteration, current_expl)) +
    geom_point(size=0.5) +
    geom_line(lwd = 0.5) +
    geom_point(data = sel.max, color = "red", size=0.5) +
    geom_point(data = sel.take, color = "red", size=0.5) +
    geom_text(data = sel.max, aes(iteration, current_expl, label = Ref), hjust=-.1, size=2.5) +
    geom_text(data = sel.take, aes(iteration, current_expl, label = Ref),hjust=.85, vjust=-.75, size=2.5) +
    cowplot::theme_cowplot()+
    theme(axis.ticks.x = element_blank(), axis.text.x = element_blank(),
          axis.ticks.y = element_line(size=.2)) +
    my.theme(-0.25) +
    scale_x_continuous(breaks = seq(1, 13, 3), limits=c(1, 13)) +
    scale_y_continuous(labels = scales::percent, limits = c(0.93, 0.96),
                       position = "right") +
    theme(panel.grid.major.y = element_line(size=.2, colour = "white"),
          panel.grid.minor.y = element_line(size=.2, colour = "white")) +
    geom_segment(aes(x = 1, y = 0.93, xend = 13, yend = 0.93),
                 arrow = arrow(length = unit(0.1, "cm"))) +
    labs(x = "# of recursions",  y = "", title = "Explained variance")

  p <- ggdraw() +
    draw_plot(p1, 0, 0, 0.5, 1) +
    draw_plot(p2, 0.45, 0, 0.5, 1)

  for (i in c("svg", "eps", "png"))
  {
    ggsave(paste0(data.dir, "/kmeans-recurive-transform-explained_variance.", i),
           p, dpi = 720, height = 7, width = 15, units = "cm")
    ggsave(
      paste0("/Users/simondi/PHD/Sci/phd/presentations/2018_08_29_group_meeting/fig/", "/kmeans-recurive-transform-explained_variance.", i),
      p, dpi = 720, height = 7, width = 15, units = "cm")
  }
}


plot.cluster.sizes <- function(data.dir, dat, crit)
{
  flog.info('Plotting cluster sizes', name=logr)

  plt <-
    ggplot() +
    geom_density_ridges(
      data=dat,  aes(x = dat$K, y = dat$ClusterCount), fill="gray",
      stat = "binline", scale = .4, draw_baseline = FALSE, bins=100, alpha=.5) +
    geom_text(data=crit, aes(x=crit$Value, y=crit$ClusterCount, label=crit$Value), vjust=1.5) +
    theme_ridges() +
    hrbrthemes::theme_ipsum_rc("Helvetica") +
    colorspace::scale_fill_discrete_sequential("Blues", c1 = 20, c2 = 70, l1 = 25, l2 = 100) +
    scale_y_discrete("# clusters", expand = c(0, 1)) +
    scale_x_log10("# cells per cluster") +
    guides(fill=FALSE) +
    my.theme() +
    theme(axis.title.x = element_text(size=20),
          axis.title.y = element_text(size=20),
          axis.text.x = element_text(size=12, color="grey30"),
          axis.text.y = element_text(size=12, color=c(
            rep("grey30", 7), "red", rep("grey30", 11)
          )),
          panel.grid.major.x = element_blank(),
          panel.grid.minor = element_blank())

  plt

  for (i in c("svg", "png", "eps"))
  {
    ggsave(
      plt,
      filename=paste0(data.dir,"/",  "kmeans-fit-cluster_sizes-histogram.", i),
      width=10, height=7)
    ggsave(
      plt,
      filename=paste0("/Users/simondi/PHD/Sci/phd/presentations/2018_08_29_group_meeting/fig/",  "kmeans-fit-cluster_sizes-histogram.", i),
      width=10, height=7)
  }

}


plot.cluster.stats <- function(data.dir, dat)
{
  flog.info('Plotting cluster statistics', name=logr)

  fl.out <- paste0(data.dir, "/", "kmeans-fit-cluster_sizes-stats.tsv")
  cl <-  group_by(dat, ClusterCount) %>%
    dplyr::summarize(Quantiles = paste(sprintf("%.2f", quantile(K)/max(K)), collapse=", "))
  readr::write_tsv(x=cl,  path=fl.out)
}


(function() {
  parser <- ArgumentParser()
  parser$add_argument(
    "-f", "--folder", help = paste("folder where the kmeans clustering has been written to.",
                                   "sth like 'outfolder' or so")
  )

  opt <- parser$parse_args()
  if (is.null(opt$folder))
  {
    stop(parser$print_help())
  }

  data.dir <- "/Users/simondi/PROJECTS/target_infect_x_project/results/2-analysis/2-clustering/current"
  data.dir <- opt$folder
  lg.file <- paste0(data.dir, "/kmeans-fit-statistics-plot.log")
  flog.appender(appender.file(lg.file), name=logr)

  loglik.file <- list.files(data.dir, full.names=T, pattern="lrt_path")
  loglik.path <- read_tsv(loglik.file) %>%
    dplyr::mutate(iteration = seq(nrow(.)))

  pls <- list.files(
    data.dir,
    pattern=paste0(".*cluster_?[s|S]izes.tsv"),
    full.names=TRUE)

  flog.info('Reading cluster size data:', name=logr)
  flog.info(paste0("\n\t", paste0(collapse="\n\t", pls)), name=logr)

  dat <- purrr::map_dfr(pls, function(e) {
    fl.suf <- as.integer(str_match(string=e, pattern=".*K(\\d+).*tsv")[2])
    tab    <- readr::read_tsv(e, col_names="K", col_types="i")
    tab$ClusterCount <- fl.suf
    tab
  })
  dat <- dat %>%
    dplyr::filter(ClusterCount %in% loglik.path$current_model)

  dat$ClusterCount <- factor(dat$ClusterCount, levels=rev(sort(unique(dat$ClusterCount))))
  crit <-  group_by(dat, ClusterCount) %>%
    summarize(Min=min(K), Max=max(K)) %>%
    tidyr::gather(Criteria, Value, -ClusterCount)

  plot.explained.variance(data.dir, loglik.path)
  plot.cluster.sizes(data.dir, dat, crit)
  plot.cluster.stats(data.dir, dat)
})()
