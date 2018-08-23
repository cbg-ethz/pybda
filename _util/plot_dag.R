#!/usr/bin/env Rscript

suppressPackageStartupMessages(library(here))
suppressPackageStartupMessages(library(readr))
suppressPackageStartupMessages(library(igraph))
suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(DiagrammeR))
library(DiagrammeRsvg)
library(pipeR)
library(V8)


(function() {
  path <- here::here("fig")
  snakefile <- list.files(path, pattern = "snakeflow.tsv", full.names = TRUE)

  gr <- readr::read_tsv(snakefile, col_names=FALSE) %>%
    dplyr::filter(X1 != "all", X2 != "all") %>%
    igraph::graph_from_data_frame()

  src.idx <- which(igraph::degree(gr,mode="in") == 0)
  gr <- igraph::add_vertices(gr, 1, name="data")

  data.idx <- which(V(gr)$name == "data")
  for (s in src.idx) {
    gr <- igraph::add_edges(gr, c(data.idx, s))
  }

  l <- layout_as_tree(gr)

  png(paste0(path, "/snakeflow.png"), width=1000, height=800,  units = "px", pointsize = 10)
  plot(gr, vertex.size=25, vertex.color="white", vertex.label.degree=0, vertex.label.family = "Helvetica",
       vertex.shape="rectangle", vertex.frame.color="white",
       vertex.label.cex=1.21, vertex.label.dist=0, vertex.label.color="black",
       edge.color="black", edge.width=.5, edge.arrow.size=.65, layout= layout_as_tree(gr))
  dev.off()


  gr <- gr %>%
    igraph::get.adjacency() %>%
    as.matrix() %>%
    DiagrammeR::from_adj_matrix(mode = 'directed',
                                use_diag = FALSE)

  n_nodes <- nrow(gr$nodes_df)
  node_labels <- gr$nodes_df$label
  n_edges <- nrow(gr$edges_df)

  gr$nodes_df$color <- "white"
  gr$nodes_df$fillcolor <- "white"
  gr$nodes_df$fontsize <- 8
  gr$nodes_df$penwidth <- 2
  gr$nodes_df$shape <- "square"
  gr$nodes_df$width <- .4
  gr$nodes_df$height <- .3 * .5

  gr$edges_df$color <- "darkgrey"
  gr$edges_df$fontsize <- 4
  gr$edges_df$penwidth <- 1

  render_graph(gr, layout="tree")


  s<- gr

  DiagrammeR::export_graph(gr, file_name=paste0(path, "/snakeflow.png"), file_type="png")

})()
