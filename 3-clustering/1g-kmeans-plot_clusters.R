library(dplyr)
library(dtplyr)
library(tibble)
library(ggplot2)
library(hrbrthemes)
library(ggthemr)
library(viridis)
library(cowplot)

ggthemr("fresh", "scientific")

hrbrthemes::import_roboto_condensed()
extrafont::loadfonts()

options(stringsAsFactors=FALSE)

dir <- "/Users/simondi/PROJECTS/target_infect_x_project/results/2-analysis/2-clustering/current/"

best.clusters.file  <- list.files(dir, pattern="best_clusters", full.names=TRUE)
cluster.files       <-list.files(paste(dir, "clusters", sep="/"), full.names=TRUE)
cluster.centers.file <- list.files(dir, pattern="cluster_centers", full.names=TRUE)
gene.pred.folder <- list.files(dir, pattern="gene_pathogen_prediction_count$", full.names=TRUE)
best.clusters <- readr::read_tsv(best.clusters.file, col_names=TRUE) %>% as.tbl


plot.oras <- function(gene.pred.folder)
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
  pre <- dat %>% dplyr::filter(prediction %in% best.clusters$prediction)
  genes         <- dat %>% dplyr::select(gene) %>% unique()

  oras <- list()
  for (i in best.clusters$prediction)
  {
    cluster1genes <- dplyr::filter(dat, prediction==i) %>% dplyr::select(gene) %>% unique()
    oras[[paste(i)]] <- ora(cluster1genes$gene, genes$gene)
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

plot.best.clusters <- function()
{
  best.clusters <- readr::read_tsv(best.clusters.file, col_names=TRUE) %>% as.tbl

  fls <- lapply(best.clusters$prediction, function(i)
  {
    idx <- grep(paste0(dir, "/clusters/.*_", i, ".*tsv"), cluster.files)
    cluster.files[idx]
  }) %>% unlist

  dat <- rbindlist(lapply(fls, function(f) readr::read_tsv(f, col_names=TRUE))) %>%
    as_tibble %>%
    tidyr::separate(features, into=paste0("Factor", 1:15), sep=",") %>%
    dplyr::mutate(Factor1:=as.double(Factor1),
                  Factor2:=as.double(Factor2),
                  prediction=as.factor(prediction))

  plt <-
    ggplot(dat) +
    geom_point(aes(x=Factor1, y=Factor2, color = prediction, shape=prediction), size=.75) +
    hrbrthemes::theme_ipsum_rc() +
    ggplot2::theme(axis.text.x  = ggplot2::element_text( size=18),
                   axis.text.y  = ggplot2::element_text(size=18),
                   axis.title.x   = ggplot2::element_text(size=20),
                   axis.title.y   = ggplot2::element_text(size=20)) +
    viridis::scale_colour_viridis(discrete=T, guide=FALSE, option="D") +
    guides(shape=FALSE)

  plot.out  <- sub(".tsv", "", best.clusters.file)
  ggsave(paste(plot.out, "genes.eps", sep="-"), plot=plt)
  ggsave(paste(plot.out, "genes.png", sep="-"), dpi=1080)
}

plot.sampled.genes <- function(sampled.genes.file)
{

  full.tbl <- readr::read_tsv(sampled.genes.file, col_names=TRUE) %>% as.tbl %>%
    tidyr::separate(features, into=paste0("Factor", 1:15), sep=",") %>%
    dplyr::mutate(Factor1:=as.double(Factor1),
                  Factor2:=as.double(Factor2),
                  prediction=as.factor(prediction))

  plt <- ggplot(full.tbl) +
    geom_point(aes(x=Factor1, y=Factor2, color = gene)) +
    hrbrthemes::theme_ipsum_rc() +
    ggplot2::theme(axis.text.x  = ggplot2::element_text( size=18),
                   axis.text.y  = ggplot2::element_text(size=18),
                   axis.title.x   = ggplot2::element_text(size=20),
                   axis.title.y   = ggplot2::element_text(size=20)) +
    viridis::scale_colour_viridis(discrete=T, guide=FALSE, option="D")

  plot.out  <- sub(".tsv", "-scatter_plot", sampled.genes.file)
  ggsave(paste(plot.out, "genes.eps", sep="-"), plot=plt)
  ggsave(paste(plot.out, "genes.png", sep="-"), dpi=450)
}

plot.best.clusters()
plot.sampled.genes(gene.pred.folder)
plot.oras(gene.pred.folder)
