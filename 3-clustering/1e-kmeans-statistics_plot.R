library(dplyr)
library(dtplyr)
library(tidyr)
library(data.table)
library(tibble)
library(ggplot2)
library(hrbrthemes)
library(ggthemr)
library(viridis)
library(cowplot)

ggthemr("fresh", "scientific")

hrbrthemes::import_roboto_condensed()
extrafont::loadfonts()

dir <- ""
bic.file         <- list.files(dir, pattern="BIC.*.tsv", full.names=TRUE)
gene.pred.folder <- list.files(dir, pattern="gene_pathogen_prediction_count$", full.names=TRUE)
silhouette.file <- list.files(dir, pattern="silhouette.tsv", full.names=TRUE)

analyse.gene.pathogen.prediction <- function(gene.pred.folder)
{
  dat <-
    rbindlist(
      parallel::mclapply(list.files(gene.pred.folder, pattern="part-", full.names=TRUE),
             function(e) { data.table::fread(e, sep="\t", header=TRUE) }, mc.cores=3 ))

  gene.pathogen.combinations <- group_by(dat, gene, pathogen) %>%
    dplyr::summarize(n=n()) %>%
    ungroup

  dat <- dplyr::left_join(dat, gene.pathogen.combinations, by=c("gene", "pathogen"))
  dat <- dplyr::mutate(dat, Frequency=count/n)

  hs <- hist(dat$Frequency, breaks=300, plot=FALSE)
  df <- data.frame(Frequency=hs$mids, Density=hs$counts/sum(hs$counts))
  fre <- mean(dat$Frequency)
  plt <-
    ggplot(df) +
    geom_histogram(aes(x=Frequency, y=Density), stat="identity") +
    hrbrthemes::theme_ipsum_rc() +
    scale_x_continuous(limits=c(0, 0.015), breaks=seq(0, 0.05, by=0.01)) +
    ylab("Density") +
    xlab("Relative frequency of single-cells mapping to same cluster") +
    labs(caption="The plot shows the relative frequency if single-cells of the same\ngenetic knockdown and pathogen map to the same cluster.") +
    geom_vline(data=dat, aes(xintercept=fre), color="red", lwd=1) +
    geom_text(aes(x=fre, y=.15), label=paste0("Mean=", round(fre, 3)), hjust=-.25) +
    ggplot2::theme(axis.text.x  = ggplot2::element_text( size=18),
                   axis.text.y  = ggplot2::element_text(size=18),
                   plot.caption  = ggplot2::element_text(size=14),
                   axis.title.x   = ggplot2::element_text(size=20),
                   axis.title.y   = ggplot2::element_text(size=20))

  ggsave(filename=paste0(gene.pred.folder, "_frequencies2.eps"), plot=plt, device="eps", width=12, height=7)
  ggsave(filename=paste0(gene.pred.folder, "_frequencies2.png"), plot=plt, device="png", width=7, height=7, dpi=1080)
}


silhouette.plot <- function(silhouette.file)
{
  dat <- fread(silhouette.file,  sep="\t", header=TRUE) %>%
    rename(Cluster = "#Cluster")
  hs <- hist(dat$Silhouette, plot=FALSE, breaks=100)
  neg.mids.idxs <- which(hs$mids <= 0)
  pos.mids.idxs <- which(hs$mids > 0)
  scors <- c(hs$mids[neg.mids.idxs], hs$mids[pos.mids.idxs])
  freqs <- c(-hs$counts[neg.mids.idxs]/sum(hs$counts), hs$counts[pos.mids.idxs]/sum(hs$counts))
  trends <- c(rep("Negative", length(neg.mids.idxs)),
              rep("Postive", length(pos.mids.idxs)))
  df <- data.frame(Silhouette=scors, Frequency=freqs, Trend=trends)

  plt <-
    ggplot(df) +
    geom_bar(stat = "identity", aes(x=Silhouette, y=Frequency, fill=Trend)) +
    scale_fill_manual(values=swatch()[c(2,4)]) +
    xlab("Silhouette score") +
    ylab("Relative frequency") +
    hrbrthemes::theme_ipsum_rc() +
    scale_x_continuous(limits=c(-0.25, .75)) +
    scale_y_continuous(limits=c(-0.05, 0.05),
      breaks=c(-0.05, -0.025, 0, 0.025, 0.05),
                      labels=abs(c(-0.05, -0.025, 0, 0.025, 0.05))) +
    ggplot2::theme(axis.text.x  = ggplot2::element_text( size=18),
                   axis.text.y  = ggplot2::element_text(size=18),
                   plot.caption  = ggplot2::element_text(size=14),
                   axis.title.x   = ggplot2::element_text(size=20),
                   legend.position="bottom",
                   legend.title=element_blank(),
                   legend.text=element_text(size=14),
                   axis.title.y   = ggplot2::element_text(size=20)) +
    coord_flip()

    outfi <- sub(".tsv", "", silhouette.file)
    ggsave(filename=paste0(outfi, ".eps"), plot=plt, device="eps")
    ggsave(filename=paste0(outfi, ".png"), plot=plt, device="png", dpi=1080)
}

write.table <- function(gene.pred.folder)
{
  dat <-
    rbindlist(
      parallel::mclapply(list.files(gene.pred.folder, pattern="part-", full.names=TRUE),
             function(e) { data.table::fread(e, sep="\t", header=TRUE) }, mc.cores=3 ))
  gene.pathogen.combinations <- group_by(dat, gene, pathogen) %>%
    dplyr::summarize(n=n()) %>%
    ungroup

  dat <- dplyr::left_join(dat, gene.pathogen.combinations, by=c("gene", "pathogen"))
  dat <- dplyr::mutate(dat, Frequency=count/n) %>% arrange(-Frequency)

  D <-
      dplyr::filter(dat, gene %in% c("mock", "none", "cdc42", "met", "mtor",
                                     "alk", "ilk", "rip4k", "pik3r3", "igf2r",
                                     "gak", "ulk1", "ntpcr", "etnk1", "wnk1",
                                     "tgfbr1")) %>%
      dplyr::group_by(gene, prediction) %>%
      dplyr::summarize(n=n()) %>%
      dplyr::group_by(gene) %>%
      dplyr::summarize(freqstr=paste0(n, "/" , n()), freq=n/n(), cnt=n()) %>%
      dplyr::group_by(gene) %>%
      arrange(-cnt) %>%
      dplyr::summarize(MaxFrequenctInBucket=freq[1])

    best.genes <- dat %>% dplyr::filter(!gene  %in% c("ran", "allstarsdeath",
                                                      "allstars hs cell death sirna")) %>%
      dplyr::group_by(gene, prediction) %>%
      dplyr::summarize(n=n()) %>%
      dplyr::group_by(gene) %>%
      dplyr::summarize(freqstr=paste0(n, "/" , n()), freq=n/n(), cnt=n()) %>%
      dplyr::group_by(gene) %>%
      arrange(-cnt) %>%
      dplyr::summarize(MaxFrequenctInBucket=freq[1]) %>%
      arrange(-MaxFrequenctInBucket) %>% .[1:20]

    best.clusters <- dat %>% dplyr::filter(!gene  %in%
            c("ran", "allstarsdeath", "allstars hs cell death sirna")) %>%
        dplyr::select(prediction) %>% unique %>% .[1:5]

    fwrite(D, paste0(gene.pred.folder, "_sample_genes_frequency_ramo.tsv"))
    fwrite(best.genes, paste0(gene.pred.folder, "_sample_genes_frequency_best.tsv"))
    fwrite(best.clusters, paste0(gene.pred.folder, "_best_clusters.tsv"))
}


analyse.gene.pathogen.prediction(gene.pred.folder)
silhouette.plot(silhouette.file)
write.table(gene.pred.folder)
