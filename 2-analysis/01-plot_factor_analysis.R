library(dplyr)
library(dtplyr)
library(tibble)
library(ggplot2)
library(hrbrthemes)
library(ggthemr)
library(viridis)
library(cowplot)

theme <- ggthemr("fresh", "scientific")
hrbrthemes::import_roboto_condensed()

options(stringsAsFactors=FALSE)

dir <- "./query_data/"
likelhood.file <- list.files(dir, pattern="likelihood.tsv", full.names=TRUE)
factors.file   <- list.files(dir, pattern="factors.tsv", full.names=TRUE)
plotout <- sub(".tsv", "",likelhood.file)

plot.likelihood <- function()
{

  full.tbl <- readr::read_tsv(likelhood.file, col_names=FALSE) %>%
    as.tbl %>%
    dplyr::mutate(Iteration=0:(n()-1)) %>%
    as.data.frame
  full.tbl$X1 <- -full.tbl$X1
  full.tbl <- full.tbl[-1,]

  plt <-
    ggplot2::ggplot(full.tbl, aes(x=Iteration, y=X1)) +
    ggplot2::geom_line(size=1.5) +
    xlab("Iteration") +
    ylab(expression(paste("-\u2113(", theta, ")"))) +
    labs(title="Factor analysis likelihood path") +
    hrbrthemes::theme_ipsum_rc() +
    ggplot2::theme(axis.text.x  = ggplot2::element_text( size=18),
                   axis.text.y  = ggplot2::element_text(size=18),
                   axis.title.x   = ggplot2::element_text(size=20),
                   axis.title.y   = ggplot2::element_text(size=20),
                   panel.grid.major.x = element_line(colour = 'black', linetype = 'dotted'))

  ggsave(paste(plotout, "likelihood_path.png", sep="-"), dpi=720)

}

plot.factors <- function()
{

  full.tbl <- readr::read_tsv(factors.file, col_names=TRUE) %>%
    as.data.frame %>%
    as.matrix %>% t

  P <- nrow(full.tbl)
  C <- ncol(full.tbl)

  vars.explained <- apply(full.tbl, 2, function(e) sum(e**2) / P)
  X <- data.frame(Factors=factor(1:length(vars.explained)), Variance=vars.explained,
                  Cumulative=cumsum(vars.explained))

  plt <-
    ggplot(X) + geom_bar(aes(x=Factors, y=Cumulative), stat="identity") +
    geom_text(aes(x=Factors, y=Cumulative, label=sprintf("%0.2f", Cumulative)), vjust=1.1, stat="identity") +
    ylab("Cumulative variance") +
    labs(title="Factor loadings variance explained") +
    hrbrthemes::theme_ipsum_rc() +
    ggplot2::theme(axis.text.x  = ggplot2::element_text( size=18),
                   axis.text.y  = ggplot2::element_text(size=18),
                   axis.title.x   = ggplot2::element_text(size=20),
                   axis.title.y   = ggplot2::element_text(size=20),
                   panel.grid.major.x = element_line(colour = 'black', linetype = 'dotted'))
  ggsave(paste(plotout, "variance_explained.eps", sep="-"), dpi=720)


  X <- data.frame(Feature=rownames(full.tbl), Factor1=full.tbl[,1], Factor2=full.tbl[,2])
  plt <-
    ggplot2::ggplot(X, aes(x=Factor1, y=Factor2)) +
    ggplot2::geom_text(aes(label = Feature), size=2) +
    ggplot2::geom_segment(aes(x=0, y=0, xend=Factor1, yend=Factor2),
                          data=X, color=theme$palette$swatch[2], alpha=.7,
                          linetype="dashed",
                          arrow = arrow(length = unit(0.25,"cm") )) +
    hrbrthemes::theme_ipsum_rc() +
    ggplot2::theme(axis.text.x  = ggplot2::element_text( size=18),
                   axis.text.y  = ggplot2::element_text(size=18),
                   axis.title.x   = ggplot2::element_text(size=20),
                   axis.title.y   = ggplot2::element_text(size=20),
                   panel.grid.major.x = element_line(colour = 'black', linetype = 'dotted'))

  ggsave(paste(plotout, "biplot.png", sep="-") , dpi=720)

}

plot.likelihood()
plot.factors()
