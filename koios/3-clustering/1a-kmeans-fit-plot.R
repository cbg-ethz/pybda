


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

  plot.cluster.sizes(data.dir, dat, crit)
  plot.cluster.stats(data.dir, dat)
})()
