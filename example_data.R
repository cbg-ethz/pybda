library(data.table)
library(dplyr)

pathogens <- c("brucella", "adeno", "salmonella", "rhino",
              "vaccinia", "listeria", "shigella")
replicates <- 1:3
library_vendor <- c("ambion", "dharmacon", "quiagen")
library_type <- c("pooled", "arrayed")
well_rows <- 1:16
well_cols <- 1:24
image <- 1:9
cell_nmb <- 1:1000
features <- c("infection_index", "neighbour_cnt", "cell_density", "cell_size")

data <- data.table(),
                   replicate=1,
                   library_vendor="ambion", library_type="pooled",
                   plate=floor(runif(7, 1, 100)),
                   well_row=floor(runif(7, 1, 16)),
                   well_col=floor(runif(7, 1, 24)),
                   image=floor(runif(7, 1, 9)),
                   cell_nmb=floor(runif(7, 0, 1000)),
                   infection_index=rnorm(7, 10, 4))
