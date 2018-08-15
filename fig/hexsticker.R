library(ggplot2)
library(viridis)
library(colorspace)
library(here)
library(reshape2)

n  <- 100 * 100
set.seed(23)
m <- sample(c(rnorm(n/2, -3, 5), rnorm(n/2, 3, 5))) %>%
  matrix(., sqrt(n))

df <-  melt(m)
# TODO: write biospark into text
#
p <- ggplot(df) +
  geom_tile(aes(Var2, Var1, fill=value)) +
  viridis::scale_fill_viridis(option="D")+
  scale_x_discrete(expand=c(0,0)) +
  scale_y_discrete(expand=c(0,0)) +
  theme_void() +
  theme(axis.text = element_blank(),
        axis.title = element_blank(),
        aspect.ratio=1) +
  guides(fill=FALSE)
p

ggsave(paste0(here::here(), "/fig/sticker.png"), p, width=5, height=5, dpi=720)
ggsave(paste0(here::here(), "/fig/sticker.pdf"), p, width=5, height=5, dpi=720)
