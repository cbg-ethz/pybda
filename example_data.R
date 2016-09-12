library(data.table)
library(dplyr)
library(gridExtra)

ttheme_default(base_size=6)

pathogens <- c("brucella", "adeno", "salmonella", "rhino",
              "vaccinia", "listeria", "shigella")
replicates <- 1:3
library_vendor <- c("ambion", "quiagen")
library_type <- c("arrayed")
well_rows <- 1:16
well_cols <- 1:24
image <- 1:9
cell_nmb <- 1:1000
features <- c("infection_index", "neighbour_cnt", "cell_density", "cell_size")
plate_idx <- 1:200
well_idx <- 1:138
sirna    <- paste("s", 1:1E6, sep="")

nrow <- 1000000
nrow <- nrow - nrow %% length(pathogens)

data <- data.table(
      pathogen=     sample(pathogens, nrow, replace=T),
      replicate=    sample(replicates, nrow, replace=T),
      library_vendor=sample(library_vendor, nrow, replace=T),
      library_type=sample(library_type, nrow, replace=T),
      sirna=sample(sirna, nrow, replace=T),
      plate_idx=sample(plate_idx, nrow, replace=T),
      well_idx=sample(well_idx, nrow, replace=T),
      well_rows=sample(well_rows,  nrow, replace=T),
      well_cols=sample(well_cols,  nrow, replace=T),
      cell_idx=sample(cell_nmb,  nrow, replace=T),
      image_idx=sample(image,  nrow, replace=T),
      infection_index=rnorm(nrow, 100, 10),
      neighbour_cnt=rnorm(nrow, 10, 5),
      cell_density=rnorm(nrow, 5, 1),
      cell_size=rnorm(nrow, 15, 3)
)


data[, .SD[sample(.N, 1)],
     by=c("pathogen"),
     .SDcols=c("replicate", "sirna", "plate_idx", "well_idx",
               "image_idx", "cell_idx", "infection_index")] %>%
  tableGrob(rows=NULL, theme = ttheme_default(base_size=8)) %>%
  grid.arrange

