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

suppressWarnings(ggthemr("fresh", "scientific"))
suppressMessages(hrbrthemes::import_roboto_condensed())


#' @description Create a table where every row counts
#'  how many single cells belong to every gene-pathogen group
.get.cell.count.per.gene.pathogen.group <- . %>%
  group_by(gene, pathogen) %>%
  dplyr::summarize(n=sum(count)) %>%
  ungroup()


#' @description Compute a table where every row shows the frequency
#' of a single cell belonging to a specific gene-pathogen group maps to a cluster
#' I.e: what is the frequency of a gene-pathogen group in a cluster
.compute.cell.cluster.frequencies <- function(dat, gpc)
{
  dat <- dplyr::left_join(dat, gpc, by=c("gene", "pathogen"))
  dat <- dplyr::mutate(dat, Frequency=count/n) %>%
    arrange(-Frequency)
  dat
}


analyse.gene.pathogen.prediction <- function(gene.pred.file)
{
  dat <- data.table::fread(gene.pred.file, sep="\t", header=TRUE)

  gene.pathogen.combinations <- .get.cell.count.per.gene.pathogen.group(dat)
  dat <- .compute.cell.cluster.frequencies(
    dat, gene.pathogen.combinations)

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


create.table <- function(gene.pred.file)
{
  dat <- data.table::fread(gene.pred.file, sep="\t", header=TRUE)
  gene.pathogen.combinations <- .get.cell.count.per.gene.pathogen.group(dat)
  dat <- .compute.cell.cluster.frequencies(
    dat, gene.pathogen.combinations)

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

  # creates clusters by their highest 'consistency' of gene-pathogen pairs mapping
  best.clusters <- dat %>%
    arrange(desc(Frequency)) %>%
    dplyr::filter(!gene  %in% c("ran", "allstarsdeath", "allstars hs cell death sirna")) %>%
    dplyr::select(prediction) %>%
    unique()

  outfl <- stringr::str_match(gene.pred.file, "(.*).tsv")[2]
  fwrite(best.genes, paste0(outfl, "-best_gene_buckets.tsv"), sep = "\t")
  fwrite(best.clusters, paste0(outfl, "-best_cluster.tsv"), sep = "\t")

  list(best.clusters = best.clusters,
       best.genes    = best.genes)
}


ora <- function(cluster.genes, universe)
{
  .to.entrez <- function(dat)
  {
    frame.hugo <- AnnotationDbi::toTable(org.Hs.eg.db::org.Hs.egSYMBOL) %>%
      as.data.table()
    dat <- dplyr::left_join(data.table(symbol=toupper(dat)), frame.hugo, by="symbol") %>%
      dplyr::filter(!is.na(gene_id))
    dat
  }

  suppressPackageStartupMessages(library(GOstats))
  hit.list <- .to.entrez(cluster.genes)
  universe <- .to.entrez(universe)
  GOparams <- new("GOHyperGParams",
                  geneIds = unique(hit.list),
                  universeGeneIds = unique(universe),
                  annotation="hgu95av2.db",
                  ontology="BP",
                  pvalueCutoff=0.05,
                  conditional=TRUE,
                  testDirection="over")
  ora <- GOstats::hyperGTest(GOparams)

  test.count <- length(ora@pvalue.order)
  summ <- summary(ora)
  pvals <- c(summ$Pvalue, rep(1, test.count - nrow(summ)))
  qvals <- p.adjust(pvals, method="BH")
  summ$Qvalue <- qvals[1:nrow(summ)]
  li <- list(ora=ora, summary=summ)

  li
}


plot.oras <- function(best.cluster, gene.pred.file, how.many.clusters=5)
{
  which.clusters <- best.clusters$prediction[seq(how.many.clusters)]

  dat <- data.table::fread(gene.pred.file, sep="\t", header=TRUE)
  gene.pathogen.combinations <- .get.cell.count.per.gene.pathogen.group(dat)
  dat <- .compute.cell.cluster.frequencies(dat, gene.pathogen.combinations)

  pre   <- dat %>% dplyr::filter(prediction %in% which.clusters)

  universe <- dat %>% dplyr::pull(gene) %>% unique()
  oras <- list()
  for (i in which.clusters)
  {
    cluster.genes <- dplyr::filter(pre, prediction==i) %>%
      pull(gene) %>% unique()
    oras[[paste(i)]] <- ora(cluster.genes, genes)
  }

  oras.flast <- rbindlist(lapply(1:length(oras), function(e) data.table(Index=e,  oras[[e]]$summary[1:10, ])))
  oras.flast <- oras.flast %>% as.data.frame
  oras.flast <- oras.flast[oras.flast$Qvalue <= .05, c("Index", "Qvalue", "Term")]

  dat <- spread(oras.flast, Index, Qvalue) %>% gather(Term)
  colnames(dat) <- c("Term", "Cluster", "Qvalue")
  dat$Qvalue[is.na(dat$Qvalue)] <- 1
  dat$Term <- factor(dat$Term, levels=rev(unique(dat$Term)))
  dat <- dplyr::mutate(dat, Significant = Qvalue <= 0.05)
  dat <-
    dplyr::group_by(dat, Term) %>%
    dplyr::mutate(S=sum(Significant)) %>%
    ungroup %>%
    dplyr::mutate(Color=( S==1 & Significant==TRUE))
  dat$Color <- factor(dat$Color)

  ggplot(dat, aes(Cluster, Term), fill="black") +
    hrbrthemes::theme_ipsum_rc() +
    geom_point(aes(size=Significant, color=Color)) +
    scale_size_discrete(name="Q-value < .05") +
    scale_color_manual(name="Exclusively significant\nwithin term", values=c("black", cols[2])) +
    ylab("GO-term") +
    ggplot2::scale_x_discrete(expand = c(0,1)) +
    ggplot2::scale_y_discrete(expand = c(0,1)) +
    ggplot2::theme(
      axis.title.y=element_blank(),
      axis.title.x=element_text(size=17, hjust=.5),
      axis.text.y=element_text(size=15),
      axis.text.x=element_blank(),
      legend.text=element_text(size=15),
      legend.title=element_text(size=17)) +
    guides(size=guide_legend("Q-value \u2264 .05", override.aes=list(colour="black")))

  ggsave(paste0(dir, "best_5_clusters_ora.eps"), dpi=2000, width=20)
  ggsave(paste0(dir, "best_5_clusters_ora.png"), dpi=1000, width=13)
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

  tabs <- create.table(gene.pred.file)
  plot.oras(tabs$best.clusters, gene.pred.file)

})()
