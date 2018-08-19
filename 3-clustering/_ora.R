suppressPackageStartupMessages(library(AnnotationDbi))
suppressPackageStartupMessages(library(GOstats))


ora <- function(cluster.genes, universe)
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

