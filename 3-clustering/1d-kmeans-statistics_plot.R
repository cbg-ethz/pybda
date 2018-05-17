#!/usr/bin/env Rscript

suppressPackageStartupMessages(library(argparse))
suppressPackageStartupMessages(library(stringr))
suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(dtplyr))
suppressPackageStartupMessages(library(tidyr))
suppressPackageStartupMessages(library(data.table))
suppressPackageStartupMessages(library(tibble))
suppressPackageStartupMessages(library(ggplot2))
suppressPackageStartupMessages(library(hrbrthemes))
suppressPackageStartupMessages(library(ggthemr))
suppressPackageStartupMessages(library(viridis))
suppressPackageStartupMessages(library(cowplot))

ggthemr("fresh", "scientific")

hrbrthemes::import_roboto_condensed()


analyse.gene.pathogen.prediction <- function(gene.pred.file)
{
  dat <- data.table::fread(gene.pred.file, sep="\t", header=TRUE)

  gene.pathogen.combinations <- group_by(dat, gene, pathogen) %>%
    dplyr::summarize(n=n()) %>%
    ungroup()

  dat <- dplyr::left_join(dat, gene.pathogen.combinations, by=c("gene", "pathogen"))
  dat <- dplyr::mutate(dat, Frequency=count/n)

  hs <- hist(dat$Frequency, breaks=300, plot=FALSE)
  df <- data.frame(Frequency=hs$mids, Density=hs$counts/sum(hs$counts))
  fre <- mean(dat$Frequency)
  plt <-
  ggplot(df) +
    geom_histogram(aes(x=Frequency, y=Density), stat="identity", fill="darkgrey") +
    hrbrthemes::theme_ipsum_rc(base_family = "Helvetica") +
    ylab("Density") +
    xlab("Relative frequency of single-cells mapping to same cluster") +
    labs(caption=paste("The plot shows the relative frequency if single-cells of the same",
                       "genetic knockdown and pathogen map to the same cluster.", sep="\n")) +
    geom_vline(data=NULL, aes(xintercept=fre), color="red", lwd=1) +
    geom_text(data=NULL, aes(x=fre, y=.15), label=paste0("Mean=", round(fre, 3)), hjust=-.25) +
    ggplot2::theme(axis.text.x  = ggplot2::element_text( size=18, color="black"),
                   axis.text.y  = ggplot2::element_text(size=18, color="black"),
                   panel.grid.minor = element_blank(),
                   plot.caption  = ggplot2::element_text(size=14, color="black"),
                   axis.title.x   = ggplot2::element_text(size=20),
                   axis.title.y   = ggplot2::element_text(size=20))

  gene.pred.folder <- stringr::str_match(string=gene.pred.file, pattern="(.*).tsv")[2]
  for (i in c("eps", "png", "svg"))
  {
    ggsave(filename=paste0(gene.pred.folder, "-frequencies.", i),
           plot=plt, device=i, width=12, height=7, dpi=1080)
  }
}


silhouette.plot <- function(silhouette.file)
{
  dat <- fread(silhouette.file,  sep="\t", header=TRUE) %>%
    rename(Cluster = "#Cluster")
  hs <- hist(dat$Silhouette, plot=FALSE, breaks=100)
  neg.mids.idxs <- which(hs$mids <= 0)
  pos.mids.idxs <- which(hs$mids > 0)
  scors <- c(hs$mids[neg.mids.idxs], hs$mids[pos.mids.idxs])
  freqs <- c(-hs$counts[neg.mids.idxs]/sum(hs$counts),
             hs$counts[pos.mids.idxs]/sum(hs$counts))
  trends <- c(rep("Negative", length(neg.mids.idxs)),
              rep("Postive", length(pos.mids.idxs)))
  df <- data.frame(Silhouette=scors, Frequency=freqs, Trend=trends)

  plt <- ggplot(df)
  if (length(unique(df$Trend)) != 1)
    plt <- plt + geom_bar(stat = "identity", aes(x=Silhouette, y=Frequency, fill=Trend))
  if (length(unique(df$Trend)) == 1)
    plt <- plt + geom_bar(stat = "identity", aes(x=Silhouette, y=Frequency), fill="darkgrey")
  plt <- plt +
    scale_fill_manual(values=swatch()[c(4,2)], labels=c("Negative", "Positive")) +
    xlab("Silhouette score") +
    ylab("Relative frequency") +
    hrbrthemes::theme_ipsum_rc(base_family = "Helvetica")
  if (length(unique(df$Trend)) != 1)
    plt <- plt +
      scale_x_continuous(limits=c(-max(abs(df$Silhouette)), max(abs(df$Silhouette)))) +
      scale_y_continuous(limits=c(-max(df$Frequency), max(df$Frequency)),
                         breaks=seq(from=-round(max(df$Frequency), digits=2), to=round(max(df$Frequency), digits=2), length.out=5),
                         labels=abs(seq(from=-round(max(df$Frequency), digits=2), to=round(max(df$Frequency), digits=2), length.out=5)))
  plt <- plt +
    ggplot2::theme(axis.text.x  = ggplot2::element_text( size=18),
                   axis.text.y  = ggplot2::element_text(size=18),
                   plot.caption  = ggplot2::element_text(size=14),
                   axis.title.x   = ggplot2::element_text(size=20),
                   legend.position="bottom",
                   panel.grid.minor = element_blank(),
                   panel.grid.major.x = element_blank(),
                   legend.title=element_blank(),
                   legend.text=element_text(size=14),
                   axis.title.y   = ggplot2::element_text(size=20)) +
    coord_flip()

  outfi <- sub(".tsv", "", silhouette.file)
  for (i in c("eps", "png", "svg"))
  {
    ggsave(filename=paste0(outfi, ".", i),
           plot=plt, device=i, width=12, height=7, dpi=1080)
  }
}


write.table <- function(gene.pred.file)
{
  dat <- data.table::fread(gene.pred.file, sep="\t", header=TRUE)

  # create a table with how many single cless belong are in ever gene-pathogen group
  gene.pathogen.combinations <- group_by(dat, gene, pathogen) %>%
    dplyr::summarize(n=sum(count)) %>%
    ungroup()
  dat <- dplyr::left_join(dat, gene.pathogen.combinations, by=c("gene", "pathogen"))
  # compute frequencies how often a single cell is in the same gene=pathogen-prediction group
  dat <- dplyr::mutate(dat, Frequency=count/n) %>% arrange(-Frequency)

  # Here we try to get the genes that are most dominant in a single cluster
  # i.e.: which genes have the hightest frequency of being in the SAME cluster
  best.genes <- dat %>%
    dplyr::filter(!gene  %in% c("ran", "allstarsdeath", "allstars hs cell death sirna")) %>%
    dplyr::group_by(gene, prediction) %>%
    dplyr::summarize(n=sum(count)) %>%
    dplyr::group_by(gene) %>%
    dplyr::summarize(freq=n/sum(n), cnt=sum(n)) %>%
    dplyr::group_by(gene) %>%
    dplyr::summarize(MaxFrequenctInBucket=freq[1]) %>%
    arrange(-MaxFrequenctInBucket)

  # write clusters by their highest 'consistency' of gene-pathogen pairs mapping
  best.clusters <- dat %>%
    arrange(desc(Frequency)) %>%
    dplyr::filter(!gene  %in% c("ran", "allstarsdeath", "allstars hs cell death sirna")) %>%
    dplyr::select(prediction) %>%
    unique()

  outfl <- stringr::str_match(gene.pred.file, "(.*).tsv")[2]
  fwrite(best.genes, paste0(outfl, "-best_gene_buckets.tsv"), sep = "\t")
  fwrite(best.clusters, paste0(outfl, "-best_cluster.tsv"), sep = "\t")
}


(run <- function() {
  parser <- ArgumentParser()
  parser$add_argument(
    "-g", "--prediction", help = paste("tsv file that contains gene-pathogen predictions, e.g.",
                      "sth like 'kmeans-transformed-statistics-gene_pathogen_prediction_counts.tsv'")
    )
  parser$add_argument(
    "-s", "--silhouettes", help = paste("tsv file that contains the silhouette scores, e.g.",
                      "kmeans-transformed-statistics-silhouette.tsv'"))

  opt <- parser$parse_args()
  if (is.null(opt$prediction) || is.null(opt$silhouettes))
  {
    stop(parser$print_help())
  }

  gene.pred.file <- opt$prediction
  silhouette.file <- opt$silhouettes

  analyse.gene.pathogen.prediction(gene.pred.file)
  silhouette.plot(silhouette.file)
  write.table(gene.pred.file)
})()
