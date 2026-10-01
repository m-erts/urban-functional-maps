# Runs LabourMarketAreas on one matrix twice, as published and with the pmin() change of
# r/run_lma.R, and reports whether the two partitions are identical.
#
#   Rscript r/check_patch.R data/interim/nl_od_2023.csv     (about 2 minutes)
suppressPackageStartupMessages({
  library(data.table)
  library(LabourMarketAreas)
})
a <- commandArgs(trailingOnly = TRUE)
od <- fread(a[1], colClasses = c(origin = "character", dest = "character", flow = "numeric"))
codes <- sort(unique(c(od$origin, od$dest)))
id <- setNames(seq_along(codes), codes)
lw <- data.table(community_live = as.integer(id[od$origin]), community_work = as.integer(id[od$dest]),
                 amount = od$flow)
run <- function() {
  t0 <- Sys.time()
  cl <- findClusters(LWCom = copy(lw), minSZ = 3500, minSC = 0.667, tarSZ = 25000, tarSC = 0.75)$lma$clusterList
  list(cl = cl[order(community)], secs = as.numeric(difftime(Sys.time(), t0, units = "secs")))
}
published <- run()
ns <- asNamespace("LabourMarketAreas")
src <- deparse(get("getLeastSelfContained", envir = ns))
j <- grep("LWSelf[, `:=`(msc, min(amount/amount_live, amount/amount_work)), ", src, fixed = TRUE)
stopifnot(length(j) == 1, trimws(src[j + 1]) == "by = 1:nrow(LWSelf)]")
src[j] <- sub("min(amount/amount_live, amount/amount_work)), ", "pmin(amount/amount_live, amount/amount_work))]",
              src[j], fixed = TRUE)
fast <- eval(parse(text = src[-(j + 1)]))
environment(fast) <- ns
assignInNamespace("getLeastSelfContained", fast, ns = "LabourMarketAreas")
patched <- run()
cat(sprintf("identical %s; seconds %.0f as published, %.0f with pmin()\n",
            identical(published$cl, patched$cl), published$secs, patched$secs))
