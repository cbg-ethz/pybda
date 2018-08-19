
suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(purrr))

#' @description Create a table where every row counts
#'  how many single cells belong to every gene-pathogen group
get.cell.count.per.gene.group <- function(df)
{
  df %>%
    dplyr::group_by(gene) %>%
    dplyr::summarize(n=sum(count)) %>%
    ungroup()
}


#' @description Compute a table where every row shows the frequency
#' of a single cell belonging to a specific gene-pathogen group maps to a cluster
#' I.e: what is the frequency of a gene-pathogen group in a cluster
compute.cell.cluster.frequencies <- function(dat, gpc, by)
{
  dat <- dplyr::left_join(dat, gpc, by=by)
  dat <- dplyr::mutate(dat, Frequency=count/n) %>%
    arrange(-Frequency)
  dat
}


read.gene.predictions <- function(gene.pred.fold)
{
  purrr:::map_dfr(list.files(gene.pred.fold, full.names=T), function(.)
  {
    read_tsv(.)
  })
}


get.gene.stats <- function(gene.pred.fold)
{
  dat <- .read.gene.predictions(gene.pred.fold)
  gene.combinations <- .get.cell.count.per.gene.group(dat)
  dat <- .compute.cell.cluster.frequencies(
    dat, gene.combinations, "gene")

  dat
}
