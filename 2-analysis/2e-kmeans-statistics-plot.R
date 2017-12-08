library(dplyr)
library(dtplyr)
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

dir <- "/Users/simondi/PROJECTS/target_infect_x_project/results/2-analysis/2-clustering/current/"
bic.file         <- list.files(dir, pattern="BIC.*.tsv", full.names=TRUE)
gene.pred.folder <- list.files(dir, pattern="gene_pathogen_prediction_count", full.names=TRUE)

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
    ylab("Density") +
    xlab("Relative frequency of single-cells mapping to same cluster") +
    geom_vline(data=dat, aes(xintercept=fre), color="red", lwd=1) +
    geom_text(aes(x=fre, y=.15), label=paste0("Mean=", round(fre, 3)), hjust=-.25) +
    ggplot2::theme(axis.text.x  = ggplot2::element_text( size=18),
                   axis.text.y  = ggplot2::element_text(size=18),
                   plot.caption  = ggplot2::element_text(size=14),
                   axis.title.x   = ggplot2::element_text(size=20),
                   axis.title.y   = ggplot2::element_text(size=20))
  #plt

  ggsave(filename=paste0(gene.pred.folder, "_frequencies.eps"), plot=plt, device="eps", width=12, height=7)
  ggsave(filename=paste0(gene.pred.folder, "_frequencies.png"), plot=plt, device="png", width=12, height=7, dpi=1080)

  dat

}

plot.oras <- function()
{
  genes         <- dat %>% dplyr::select(gene) %>% unique()
  oras <- list()
  for (i in c(23, 42, 121, 31, 1))
  {
    cluster1genes <- dplyr::filter(dat, prediction==i) %>% dplyr::select(gene) %>% unique()
    oras[[paste(i)]] <- ora(cluster1genes$gene, genes$gene)
  }

  oras.flast <- rbindlist(lapply(1:length(oras),
                                 function(e) data.table(Index=e,  oras[[e]]$summary[1:10, ])))
}

.to.entrez <-function(dat)
{
  frame.hugo <- AnnotationDbi::toTable(org.Hs.eg.db::org.Hs.egSYMBOL) %>%
    as.data.table
  dat <- dplyr::left_join(data.table(symbol=toupper(dat)), frame.hugo, by="symbol")

  dat
}

ora <- function(genes, universe)
{
  library(GOstats)
  hit.list <- .to.entrez(genes)
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

plot.bic <- function(bic.file)
{
  fl <- readr::read_tsv(bic.file, col_names=TRUE)
  plt <- ggplot(fl, aes(x=index, y=stat)) +
    geom_line(lwd=1, color="black") +
    geom_point(size=3) +
    geom_label(data=subset(fl,index>=5000) , aes(x=index, y=stat, label=format(floor(stat), big.mark=" ", scientific=FALSE)), size=5,  fontface = "bold", vjust=-.5) +
    hrbrthemes::theme_ipsum_rc() +
    scale_y_log10(breaks=scales::pretty_breaks(n=4)) +
    scale_x_continuous(limits=c(0, 21000)) +
    ylab("BIC") + xlab("Cluster centers") +
    ggplot2::theme(axis.text.x  = ggplot2::element_text( size=18),
                   axis.text.y  = ggplot2::element_text(size=18),
                   axis.title.x   = ggplot2::element_text(size=20),
                   axis.title.y   = ggplot2::element_text(size=20),
                   panel.grid.major.x = element_line(colour = 'black', linetype = 'dotted'))

  ggsave(filename=sub(".tsv", ".eps", bic.file), plt, width=12, height=7)
  ggsave(filename=sub(".tsv", ".png", bic.file), plt, width=12, height=7, dpi=1080)

}

#plot.bic(bic.file)
analyse.gene.pathogen.prediction(gene.pred.folder)
