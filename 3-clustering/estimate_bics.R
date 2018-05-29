library(dplyr)
library(tidyr)
library(ggthemr)
library(rutil)
library(cowplot)

fl <- "/Users/simondi/PROJECTS/target_infect_x_project/results/2-analysis/2-clustering/2018_05_27/outlier_detection-all_optimal_from_file_feature_dbq_250_cells_100_test.json"
out.fold <- "/Users/simondi/PROJECTS/target_infect_x_project/results/2-analysis/2-clustering/2018_05_27/"

dat <- readr::read_tsv(fl)

# Computation of BICs from:
#  - http://www.stat.wisc.edu/courses/st333-larget/aic.pdf
#    bic_2 =  N + N * numpy.log(2 * numpy.pi) + N * numpy.log(rss/N) + numpy.log(N) * (K + 1)
#  - https://stackoverflow.com/questions/15839774/how-to-calculate-bic-for-k-means-clustering-in-r
#    https://rdrr.io/rforge/kmeansstep/man/kmeansBIC.html
#    bic = rss + log(N) * K * P
#  - bic = N * numpy.log(rss / N) + K * numpy.log(N) ?

pl <- ggplot(gathered.dat) +
  geom_point(aes(x=K, y=Value, color=Score)) + scale_y_log10()

K <- dat$K
P <- 15
N <- 46326489
rss  <- dat$RSS

bic <- function() {
  rss + log(N) * K * P
}

bic2 <- function() {
  N + N * log(2 * pi) + N * log(rss/N) + log(N) * (K + P + 1)
}


df <- data.frame(
  K    = K,
  RSS  =  rss,
  BIC  =  bic()
)

gathered.dat <-  df[seq(2, 17),] %>%
  tidyr::gather(Score, Value, -K)

pl <-
  ggplot(gathered.dat) +
  geom_point(aes(x=K, y=Value, color=Score)) +
  geom_line(aes(x=K, y=Value, color=Score)) +
  scale_y_continuous("") +
  scale_x_continuous("# clusters") +
  scale_color_manual(values=rutil::manual_discrete_colors()[c(2, 7, 1)]) +
  hrbrthemes::theme_ipsum() +
  theme(
    panel.grid.minor = element_blank(),
    axis.title.x = element_text(size=20),
    axis.text.x = element_text(size=15),
    axis.text.y = element_text(size=15),
    axis.title.y = element_text(size=20),
    legend.text = element_text(size=20),
    legend.title = element_blank(),
    legend.position="bottom") +
  guides(color = guide_legend(override.aes = list(size = 3))) +
  labs(caption="BIC := RSS + log(N) * P * K")

for (i in c("eps", "svg", "png")) {
  ggsave(plot=pl, paste0(out.fold, "/kmeans_bic_path.", i), width=10, height=6)
}


df2 <- data.frame(
  K    = K,
  RSS  = 1 - rss/rss[1],
  BIC  = 1 - bic() / bic()[1]
)

gathered.dat2 <-  df2[seq(2, 17),] %>%
  tidyr::gather(Score, Value, -K)

pl2 <-
  ggplot(gathered.dat2) +
  geom_point(aes(x=K, y=Value, color=Score)) +
  geom_line(aes(x=K, y=Value, color=Score)) +
  scale_y_continuous("") +
  scale_x_continuous("# clusters") +
  scale_color_manual(
    values=rutil::manual_discrete_colors()[c(2, 7)],
    labels =c("Explained variance", expression(italic("Explained BIC")))) +
  hrbrthemes::theme_ipsum() +
  theme(
    panel.grid.minor = element_blank(),
    axis.title.x = element_text(size=20),
    axis.text.x = element_text(size=15),
    axis.text.y = element_text(size=15),
    axis.title.y = element_text(size=20),
    legend.text = element_text(size=20),
    legend.title = element_blank(),
    legend.position="bottom") +
  guides(override.aes = list(size = 3)) +
  labs(caption="BIC := RSS + log(N) * P * K")

for (i in c("eps", "svg", "png")) {
  ggsave(plot=pl, paste0(out.fold, "/kmeans_explained_bic_path.", i), width=10, height=6)
}
