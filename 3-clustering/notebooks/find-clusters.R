library(mlr)
library(here)
library(dplyr)
library(readr)
library(tibble)
library(ggplot2)
library(cowplot)
library(tidyr)

bic <- function(rss, N, K, P)
{
  rss + log(N) * K * P
}

bic2 <- function(rss, N, K, P)
{
  N + N * log(2 * pi) + N * log(rss/N) + log(N) * (K + P + 1)
}


.estimate <- function(f)
{
  df <- read_tsv(f) %>% as.data.frame()
  cls <- colnames(df)
  feature.cls <- which(stringr::str_detect(cls, "f_"))
  task <- mlr::makeClusterTask(data = df[ ,feature.cls])

  result <- NULL
  n.obs <- 10 ^ ceiling(log10(nrow(df)))
  k.sequence <- c(seq(2, 10), 20, 30, 40, 50, 100, 200, 300, 400, 500) * n.obs / 1000
  k.sequence <- k.sequence[ k.sequence > 1]
  for (k in k.sequence) {
    lrn <- makeLearner("cluster.kmeans", centers = k, iter.max = 25)
    el  <- train(lrn, task)
    mod <- el$learner.model
    result <- rbind(
      result,
      data.frame(
        "BIC"      = bic(mod$tot.withinss,  n.obs, k, length(feature.cls)),
        "BIC2"     = bic2(mod$tot.withinss, n.obs, k, length(feature.cls)),
        "RSS"      = mod$totss,
        "K"        = k
        )
      )
  }

  p100000 <- ggplot() +
    geom_point(data = result, aes(K, BIC2), color="black") +
    geom_point(data = result[which.min(result$BIC2), ], aes(K, BIC2), color="red") +
    geom_text(data = result[which.min(result$BIC2), ], aes(K, BIC2, label = K), color="red", vjust=-1) +
    theme_cowplot() +
    labs(title=paste("BIC for clusterings for data of size n = ", n.obs) )
  p100000
}


estimate <- function()
{
  data.folder <- "~/PHD/data/data/target_infect_x/2-analysis-subsamples/"
  fls <- list.files(data.folder, full.names = TRUE)

  plots <- list()
  for (f in fls[-1])
  {
    plots <- list(plots, .estimate(f))
  }

}

