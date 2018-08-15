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
suppressPackageStartupMessages(library(viridis))
suppressPackageStartupMessages(library(cowplot))


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


silhouette.plot <- function(silhouette.file)
{
  flog.info('Plotting silhouette scores for single cell measurements.', name=logr)

  dat <- read_tsv(silhouette.file) %>%
    rename(Cluster = "#Cluster")

  hs <- hist(dat$Silhouette, plot=FALSE, breaks=100)
  neg.mids.idxs <- which(hs$mids <= 0)
  pos.mids.idxs <- which(hs$mids > 0)
  scors <- c(hs$mids[neg.mids.idxs], hs$mids[pos.mids.idxs])
  freqs <- c(-hs$counts[neg.mids.idxs]/sum(hs$counts),
             hs$counts[pos.mids.idxs]/sum(hs$counts))
  trends <- c(rep("Negative", length(neg.mids.idxs)),
              rep("Postive", length(pos.mids.idxs)))
  df <- tibble(Silhouette=scors, Frequency=freqs, Trend=trends)

  plt <- ggplot(df)
  if (length(unique(df$Trend)) != 1)
    plt <- plt + geom_bar(stat = "identity", aes(x=Silhouette, y=Frequency), fill="darkgrey")
  if (length(unique(df$Trend)) == 1)
    plt <- plt + geom_bar(stat = "identity", aes(x=Silhouette, y=Frequency), fill="darkgrey")
  plt <- plt +
    xlab("Silhouette score") +
    ylab("Frequency") +
    hrbrthemes::theme_ipsum_rc()
  if (length(unique(df$Trend)) != 1)
    plt <- plt +
    #scale_x_continuous(limits=c(-max(abs(df$Silhouette)), max(abs(df$Silhouette)))) +
    scale_y_continuous(limits=c(-max(df$Frequency), max(df$Frequency)),
                       breaks=seq(from=-round(max(df$Frequency), digits=2), to=round(max(df$Frequency), digits=2), length.out=5),
                       labels=abs(seq(from=-round(max(df$Frequency), digits=2), to=round(max(df$Frequency), digits=2), length.out=5)))
  plt <- plt +
    ggplot2::theme(axis.text.x  = ggplot2::element_text( size=18),
                   axis.text.y  = ggplot2::element_text(size=18),
                   plot.caption  = ggplot2::element_text(size=14),
                   axis.title.x   = ggplot2::element_text(size=20),
                   legend.position="bottom",
                   panel.grid.minor.x = element_blank(),
                   panel.grid.major.x = element_blank(),
                   legend.title=element_blank(),
                   legend.text=element_text(size=14),
                   axis.title.y   = ggplot2::element_text(size=20)) +
    guides(fill=FALSE) +
    coord_flip()

  outfi <- sub(".tsv", "", silhouette.file)
  for (i in c("eps", "png", "svg"))
  {
    ggsave(filename=paste0(outfi, ".", i),
           plot=plt, device=i, width=8, height=8, dpi=1080)
  }
}


#' @description Create a table where every row counts
#'  how many single cells belong to every gene-pathogen group
.get.cell.count.per.gene.group <- . %>%
  group_by(gene) %>%
  dplyr::summarize(n=sum(count)) %>%
  ungroup()


#' @description Compute a table where every row shows the frequency
#' of a single cell belonging to a specific gene-pathogen group maps to a cluster
#' I.e: what is the frequency of a gene-pathogen group in a cluster
.compute.cell.cluster.frequencies <- function(dat, gpc, by)
{
  dat <- dplyr::left_join(dat, gpc, by=by)
  dat <- dplyr::mutate(dat, Frequency=count/n) %>%
    arrange(-Frequency)
  dat
}


.get.gene.stats <- function(gene.pred.fold)
{
  dat <- purrr:::map_dfr(list.files(gene.pred.fold, full.names=T), function(.)
  {
    read_tsv(.)
  })
  gene.pathogen.combinations <- .get.cell.count.per.gene.group(dat)
  dat <- .compute.cell.cluster.frequencies(
    dat, gene.pathogen.combinations, "gene")

  dat
}


#' @description Plots the frequencies how often a gene fits into the same cluster
plot.gene.cluster.frequency <- function(gene.pred.fold)
{

  flog.info('Computing histograms for gene pathogen predictions. ', name=logr)

  dat <- purrr:::map_dfr(list.files(gene.pred.fold, full.names=T), function(.) {
    read_tsv(.)
  })

  gene.pathogen.combinations <- .get.cell.count.per.gene.group(dat)
  dat <- .compute.cell.cluster.frequencies(
    dat, gene.pathogen.combinations, c("gene"))

  hs  <- hist(dat$Frequency, breaks=200, plot=FALSE)
  df  <- tibble(Frequency=hs$mids, Density=hs$counts/sum(hs$counts))
  fre <- mean(dat$Frequency)

  plt <-
    ggplot(df) +
    scale_x_continuous(limits=c(0 , 0.01)) +
    geom_histogram(aes(x=Frequency, y=Density),  stat="identity", fill="darkgray") +
    hrbrthemes::theme_ipsum() +
    my.theme() +
    ylab("Density") +
    xlab("Relative frequency of single-cells mapping to same cluster") +
    labs(caption=paste("The plot shows the relative frequency if single-cells of the same",
                       "genetic knockdown and pathogen map to the same cluster.", sep="\n")) +
    geom_vline(data=NULL, aes(xintercept=fre), color="red", lwd=1) +
    geom_text(data=NULL, aes(x=fre, y=.15), label=paste0("Mean=", round(fre, 3)), hjust=-.25, size=5) +
    my.theme() +
    ggplot2::theme(axis.text.x  = ggplot2::element_text( size=18, color="black"),
                   axis.text.y  = ggplot2::element_text(size=18, color="black"),
                   panel.grid.minor = element_blank(),
                   plot.caption  = ggplot2::element_text(size=14, color="black"),
                   axis.title.x   = ggplot2::element_text(size=20),
                   axis.title.y   = ggplot2::element_text(size=20))

  flog.info('Plotting histograms for gene pathogen predictions. ', name=logr)
  for (i in c("eps", "png", "svg"))
  {
    ggsave(filename=paste0(gene.pred.fold, "-frequencies.", i),
           plot=plt, device=i, width=12, height=7, dpi=1080)
  }
}


create.table <- function(gene.pred.fold)
{
  flog.info("Computing best gene and cluster tables", name=logr)
  dat            <- .get.gene.stats(gene.pred.fold)

  # Here we try to get the genes that are most dominant in a single cluster
  # i.e.: which genes have the hightest frequency of being in the SAME cluster
  best.genes <- dat %>%
    dplyr::filter(!gene  %in% c("ran", "allstarsdeath", "allstars hs cell death sirna")) %>%
    dplyr::group_by(gene) %>%
    dplyr::summarize(MaxFreq = max(Frequency)) %>%
    ungroup() %>%
    arrange(desc(MaxFreq))

  # creates clusters by their highest 'consistency' of gene-pathogen pairs mapping
  best.clusters <-
    dat %>%
    dplyr::filter(!gene  %in% c("ran", "allstarsdeath", "allstars hs cell death sirna")) %>%
    arrange(desc(Frequency)) %>%
    dplyr::select(prediction) %>%
    dplyr::distinct()

  flog.info(paste0("\twriting tables to: ", gene.pred.fold), name=logr)

  readr::write_tsv(best.genes, paste0(gene.pred.fold, "-best_gene_buckets.tsv"))
  readr::write_tsv(best.clusters, paste0(gene.pred.fold, "-best_cluster.tsv"))

  list(best.clusters = best.clusters,
       best.genes    = best.genes)
}


.ora <- function(cluster.genes, universe)
{
  .to.entrez <- function(dat)
  {
    frame.hugo <- AnnotationDbi::toTable(org.Hs.eg.db::org.Hs.egSYMBOL) %>%
      as.tibble()
    dat <- dplyr::left_join(
      tibble(symbol=toupper(dat)),
      frame.hugo, by="symbol") %>%
      dplyr::filter(!is.na(gene_id))

    dat
  }

  suppressPackageStartupMessages(library(GOstats))
  hit.list <- .to.entrez(cluster.genes)
  universe <- .to.entrez(universe)
  GOparams <- new("GOHyperGParams",
                  geneIds = unique(hit.list$gene_id),
                  universeGeneIds = unique(universe$gene_id),
                  annotation="hgu95av2.db",
                  ontology="BP",
                  pvalueCutoff=0.05,
                  conditional=TRUE,
                  testDirection="over")
  ora <- GOstats::hyperGTest(GOparams)

  test.count <- length(ora@pvalue.order)
  summ <- summary(ora)
  if (nrow(summ) != 0)
  {
    pvals <- c(summ$Pvalue, rep(1, test.count - nrow(summ)))
    qvals <- p.adjust(pvals, method="BH")
    summ$Qvalue <- qvals[1:nrow(summ)]
  }

  li <- list(ora=ora, summary=summ)

  li
}


oras <- function(which.clusters, gene.frequency.table, how.many.clusters)
{
  pre   <- gene.frequency.table %>%
    dplyr::filter(prediction %in% which.clusters)
  universe <- gene.frequency.table %>%
    dplyr::pull(gene) %>% unique()

  oras <- list()
  for (i in which.clusters)
  {
    cluster.genes <- dplyr::filter(pre, prediction==i) %>%
      dplyr::pull(gene) %>%
      unique()
    flog.info(paste('\tdoing ORAs', i), name=logr)
    oras[[paste(i)]] <- .ora(cluster.genes, universe)
  }

  oras.flat <- map_dfr(
    seq(oras),
    function(i)
    {
      cbind(Index=i,  oras[[i]]$summary) %>%
        as.tibble() %>%
        dplyr::filter(!is.na(Pvalue))
    })

  oras.flat
}


make.random.oras <- function(gene.frequency.table, how.many.clusters, subset.cnt=how.many.clusters - 1)
{
    random.oras <- purrr::map_dfr(
      seq(subset.cnt),
      function(i)
      {
        which.clusters <- sample(gene.frequency.table$prediction, 5, replace=F)
        orai <- oras(which.clusters, gene.frequency.table, how.many.clusters)
        add_column(Sample=1, orai, .before=TRUE)
      }
    )
}

plot.oras <- function(best.clusters, gene.pred.fold, how.many.clusters=10, data.dir)
{
    flog.info('Computing ORAs.', name=logr)
    gene.frequency.table <- .get.gene.stats(gene.pred.fold)
    random.oras   <- make.random.oras(gene.frequency.table, how.many.clusters - 1)

    which.clusters <- best.clusters$prediction[seq(how.many.clusters)]
    oras.flat      <- oras(which.clusters, gene.frequency.table, how.many.clusters)

    if (nrow(oras.flat) == 0) {
      flog.info('\tno significant OR was found. Writing nothing...', name=logr)
      return(NULL)
    }

    flog.info('\tplotting and writing ORA table.', name=logr)
    p <-  oras.flat[ oras.flat$Qvalue <= .01,
                     c("Index", "Qvalue", "Term")] %>%
      group_by(Term) %>%
      summarize(Count=n()) %>%
      ggplot() +
        geom_bar(aes(Count), bins=20) +
        geom_text(stat='count', aes(Count, label=..count..), vjust=-.5) +
        hrbrthemes::theme_ipsum() +
        scale_x_continuous(breaks=seq(how.many.clusters)) +
        theme(
          axis.title.x = element_text(size = 15, face = "bold"),
          axis.title.y = element_blank(),
          panel.grid = element_blank(),

          axis.text.y = element_blank()) +
       labs(x = sprintf("# same GO-term found in %d different clusters", how.many.clusters),
            y = "", title = "Frequency of GO-terms")

    for (i in c("eps", "svg", "png"))
    {
      ggsave(paste0(data.dir, "/go-term_distribution.", i), p, width=10, height=6, dpi=720)
    }




    unique.ora.terms <- oras.flat[oras.flat$Qvalue <= .01, c("Index", "Qvalue", "Term")] %>%
      dplyr::group_by(Term) %>%
      dplyr::mutate(Count=n()) %>%
      dplyr::filter(Count == 1) %>%
      dplyr::select(-Count)


    unique.ora.table <- tidyr::spread(unique.ora.terms, Index, Qvalue)
    readr::write_tsv(unique.ora.table, paste0(data.dir, "/ora-table.tsv"))

    unique.ora.table <- unique.ora.table %>%
      tidyr::gather(Cluster, Qvalue ,-Term) %>%
      dplyr::mutate(Qvalue = replace(Qvalue, is.na(Qvalue), 1))

    most.significant.terms <- unique.ora.table %>%
      dplyr::arrange(Qvalue)

    unique.ora.table <- unique.ora.table %>%
      dplyr::filter(Term %in% most.significant.terms)

    unique.ora.table$Term <- factor(
      unique.ora.table$Term, levels=rev(unique(unique.ora.table$Term)))
    unique.ora.table <- unique.ora.table %>%
      dplyr::mutate(Significant = Qvalue <= 0.05) %>%
      dplyr::group_by(Term) %>%
      dplyr::mutate(S = sum(Significant)) %>%
      ungroup() %>%
      dplyr::mutate(
        Color   = factor(S == 1 & Significant==TRUE),
        Cluster = as.character(Cluster))

    ggplot(unique.ora.table, aes(Cluster, Term), fill="black") +
      hrbrthemes::theme_ipsum_rc() +
      geom_point(aes(color=Color, size=Color)) +
      scale_color_manual(name="Significant in\nonly one cluster", values=c("black", "#65ADC2")) +
      ylab("Different clusters") +
      ylab("GO-term") +
      ggplot2::scale_x_discrete(expand = c(0, 1)) +
      ggplot2::scale_y_discrete(expand = c(0, 1)) +
      ggplot2::theme(
        axis.title.y=element_blank(),
        panel.grid.major.x=element_blank(),
        axis.title.x=element_text(size=17, hjust=.5),
        axis.text.y=element_text(size=15),
        axis.text.x=element_blank(),
        legend.text=element_text(size=15),
        legend.title=element_text(size=17))

    dir <- stringr::str_match(string=gene.pred.file, pattern="(.*).tsv")[2]
    readr::write_tsv(oras.flast, path=paste0(dir, "-", "ora.tsv"))
    for (i in c("eps", "png", "svg"))
    {
      ggsave(filename=paste0(dir, "-ora.", i),
             plot=plt, dpi=1000, width=13)
    }
}


plot.best.clusters <- function(best.clusters, dir, how.many.clusters=5)
{
  flog.info('PLotting best clusters.', name=logr)
  cluster.folder <- paste0(dir, "/kmeans-transformed-clusters/")
  cluster.files  <- list.files(cluster.folder, full.names=T)
  fls <- purrr::map_chr(best.clusters$prediction, function(i) {
    idx <- grep(paste0("/cluster-", i, ".tsv"), cluster.files)
    cluster.files[idx]
  })

  dat <- purrr::map_dfr(fls , function(f) readr::read_tsv(f, col_names=TRUE)) %>%
    dplyr::mutate(Factor1:=as.double(f_0),
                  Factor2:=as.double(f_1),
                  prediction=as.factor(prediction))

  plt <-
    ggplot(dat) +
    geom_point(aes(x=Factor1, y=Factor2, color = prediction, shape=prediction), size=.75) +
    hrbrthemes::theme_ipsum_rc() +
    xlab("Factor 1") + ylab("Factor 2") +
    ggplot2::theme(axis.text.x  = ggplot2::element_text( size=18),
                   axis.text.y  = ggplot2::element_text(size=18),
                   axis.title.x   = ggplot2::element_text(size=20),
                   axis.title.y   = ggplot2::element_text(size=20)) +
    viridis::scale_colour_viridis(discrete=T, guide=FALSE, option="D") +
    guides(shape=FALSE)

  plot.out  <- paste0(dir, "/kmeans-transformed-clusters")
  flog.info(paste0("\tplotting to: ", plot.out), name=logr)
  for (i in c("png", "svg", "eps"))
  {
    ggsave(paste0(plot.out, "-gene_clusters.", i), plot=plt, dpi=720, height=7, width=7)
  }
}


(run <- function() {
  parser <- ArgumentParser()
  parser$add_argument(
    "-f", "--folder", help = paste("tsv file that contains gene-pathogen predictions, e.g.",
                      "sth like 'kmeans-transformed-statistics-gene_pathogen_prediction_counts.tsv'")
  )

  opt <- parser$parse_args()
  if (is.null(opt$folder) || is.null(opt$silhouettes))
  {
    stop(parser$print_help())
  }

  data.dir <- "/Users/simondi/PROJECTS/target_infect_x_project/results/2-analysis/2-clustering/current"

  data.dir <- opt$folder
  lg.file  <- paste0(data.dir, "/kmeans-transformed-statistics-plot.log")
  flog.appender(appender.file(lg.file), name=logr)

  gene.pred.fold  <- list.files(data.dir, pattern="gene_prediction_counts$", full.names=T)
  silhouette.file <- list.files(data.dir, pattern="silhouette.tsv", full.names=T)

  plot.gene.cluster.frequency(gene.pred.fold)
  silhouette.plot(silhouette.file)

  tabs <- create.table(gene.pred.fold)
  plot.oras(tabs$best.clusters, gene.pred.fold, 10, data.dir)
  plot.best.clusters(tabs$best.clusters, dir)


})()
