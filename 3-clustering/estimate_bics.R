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

bic.xmeans <- function() {
  n_param <- K + P


}

df <- data.frame(
  K    = K,
  RSS  =  rss,
  BIC  =  bic(),
  BIC2 =  bic2()
)

gathered.dat <-  df[seq(2, 17),] %>%
  tidyr::gather(Score, Value, -K)

pl <-
  ggplot(gathered.dat) +
  geom_point(aes(x=K, y=Value, color=Score), size=2) +
  geom_line(aes(x=K, y=Value, color=Score), size=1) +
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
  labs(caption="BIC := RSS + log(N) * P * K\nBIC2 := N + N * log(2 * pi) + N * log(RSS/N) + log(N) * (K + P)")
pl


for (i in c("eps", "svg", "png")) {
  ggsave(plot=pl, paste0(out.fold, "/kmeans_bic_path.", i), width=10, height=6)
}


df2 <- data.frame(
  K    = K,
  RSS  = 1 - rss/rss[1],
  BIC  = 1 - bic() / bic()[1]
) %>% .[seq(2, 17),]


gathered.dat2 <-  df2[seq(2, 17),] %>%
  tidyr::gather(Score, Value, -K)

pl2 <-
  ggplot(gathered.dat2) +
  geom_point(aes(x=K, y=Value, color=Score), size=2) +
  geom_line(aes(x=K, y=Value, color=Score), size=1) +
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

pl2

for (i in c("eps", "svg", "png")) {
  ggsave(plot=pl2, paste0(out.fold, "/kmeans_explained_bic_path.", i), width=10, height=6)
}


diminishing.returns.bic <- df2$BIC[seq(2, length(df2$BIC))] -  df2$BIC[seq(1, length(df2$BIC) - 1)]
diminishing.returns.rss <- df2$RSS[seq(2, length(df2$RSS))] -  df2$RSS[seq(1, length(df2$RSS) - 1)]

df3 <- data.frame(
  BIC = diminishing.returns.bic,
  RSS = diminishing.returns.rss,
  K = df2$K[seq(2, length(df2$BIC))])


gathered.dat3 <-  df3 %>%
  tidyr::gather(Score, Value, -K)


pl3 <-
  ggplot(gathered.dat3) +
  geom_point(aes(x=K, y=Value, color=Score), size=2) +
  geom_line(aes(x=K, y=Value, color=Score), size=1) +
  #geom_text(data=subset(gathered.dat3, Score=="BIC" &  K == 2500), aes(x=K, y=Value - .0015, label=K), size=5) +
  scale_y_continuous("") +
  scale_x_continuous("# clusters") +
  scale_color_manual(
    values=rutil::manual_discrete_colors()[c(2, 7)],
    labels =c("RSS", "BIC")) +
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
  labs(caption="BIC := RSS + log(N) * P * K", title="Diminishing returns?")

pl3

for (i in c("eps", "svg", "png")) {
  ggsave(plot=pl3, paste0(out.fold, "/kmeans_diminishing.", i), width=10, height=6)
}
