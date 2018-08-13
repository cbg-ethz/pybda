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
    legend.position = legend_pos,
    legend.text = element_text(size = 8),
    legend.title = element_text(size = 8)) +
    background_grid(
      major = "y", minor = "y",
      colour.major = "grey80", colour.minor = "grey90",
      size.major = 0.2, size.minor = 0.2
    )
}


plot.explained.variance <- function(data.dir, loglik.path)
{
  flog.info('Plotting explained variance', name=logr)

  p1 <- ggplot(data = loglik.path, aes(iteration, current_model)) +
    geom_point(size = 0.5) +
    cowplot::theme_cowplot()+
    my.theme(-0.7) +
    geom_line(lwd = 0.5) +
    scale_x_continuous(breaks = seq(1, 13, 3)) +
    scale_y_continuous(breaks = seq(0, 50000, 25000),
                       limits = c(0, 51000)) +
    labs(x = "Iteration", y = "", title = "Number of clusters")
  p2 <-  ggplot(data = loglik.path, aes(iteration, current_expl)) +
    geom_point(size=0.5) +
    cowplot::theme_cowplot()+
    my.theme(-0.25) +
    geom_line(lwd = 0.5) +
    scale_x_continuous(breaks = seq(1, 13, 3)) +
    scale_y_continuous(labels = scales::percent, limits = c(0.93, 0.96),
                       position = "right") +
    labs(x = "Iteration", y = "", title = "Explained variance")

  p <- ggdraw() +
    draw_plot(p1, 0, 0, 0.5, 1) +
    draw_plot(p2, 0.5, 0, 0.5, 1)

  for (i in c("svg", "eps", "png")) {
    ggsave(paste0(data.dir, "/kmeans-recurive-transform-explained_variance.", i),
           p, dpi = 720, height = 7, width = 15, units = "cm")
  }
}


plot.cluster.sizes <- function(data.dir, dat, crit)
{
  flog.info('Plotting cluster sizes', name=logr)

  plt <-
    ggplot() +
    geom_density_ridges(
      data=dat,  aes(x = dat$K, y = dat$ClusterCount, ), fill="gray",
      stat = "binline", scale = .4, draw_baseline = FALSE, bins=100, alpha=.5) +
    geom_text(data=crit, aes(x=crit$Value, y=crit$ClusterCount, label=crit$Value), vjust=1.5) +
    theme_ridges() +
    hrbrthemes::theme_ipsum() +
    colorspace::scale_fill_discrete_sequential("Blues", c1 = 20, c2 = 70, l1 = 25, l2 = 100) +
    scale_y_discrete("# clusters", expand = c(0, 1)) +
    scale_x_log10("# cells per cluster") +
    guides(fill=FALSE) +
    my.theme() +
    theme(axis.title.x = element_text(size=20),
          axis.title.y = element_text(size=20),
          axis.text.x = element_text(size=12),
          panel.grid.major.x = element_blank(),
          panel.grid.minor = element_blank(),
          axis.text.y = element_text(size=12))

  for (i in c("svg", "png", "eps"))
  {
    ggsave(
      plt,
      filename=paste0(data.dir,"/",  "kmeans-fit-cluster_sizes-histogram.", i),
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


(run <- function() {
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

  data.dir <- opt$folder
  lg.file <- paste0(data.dir, "/kmeans-fit-statistics-plot.log")
  flog.appender(appender.file(lg.file), name=logr)

  loglik.file      <- list.files(data.dir, full.names=T, pattern="lrt_path")
  loglik.path  <- read_tsv(loglik.file) %>%
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

  dat <- dat %>% dplyr::filter(ClusterCount >= 1000)
  dat$ClusterCount <- factor(dat$ClusterCount, levels=rev(sort(unique(dat$ClusterCount))))
  crit <-  group_by(dat, ClusterCount) %>%
    summarize(Min=min(K), Max=max(K)) %>%
    tidyr::gather(Criteria, Value, -ClusterCount)

  plot.explained.variance(data.dir, loglik.path)
  plot.cluster.sizes(data.dir, dat, crit)
  plot.cluster.stats(data.dir, dat)
})()
