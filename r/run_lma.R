# Labour market areas with the Coombes-Bond algorithm as implemented by Istat
# (R package LabourMarketAreas, Franconi, D'Alo and Ichim).
#
#   Rscript r/run_lma.R <input.csv> <output.csv> <minSZ> <minSC> <tarSZ> <tarSC> [verbose]
#
# input: columns origin, dest, flow (unit codes as text). Output: unit, area, residents; and next to it
# <output>_run.csv with the number of units and areas, the run time and the versions.
# Parameters of the official Travel to Work Areas 2011: 3500 0.667 25000 0.75.
suppressPackageStartupMessages({
  library(data.table)
  library(LabourMarketAreas)
})
# Speed only. getLeastSelfContained takes the smaller of the two self-containment values with a
# per-row grouping (by = 1:nrow(LWSelf)), which dominates the run time on large matrices. pmin()
# gives the same values: the Dutch and Spanish partitions are identical with and without this
# change (r/check_patch.R reruns the comparison). The check below stops if the package text is not
# the one patched.
ns <- asNamespace("LabourMarketAreas")
src <- deparse(get("getLeastSelfContained", envir = ns))
j <- grep("LWSelf[, `:=`(msc, min(amount/amount_live, amount/amount_work)), ", src, fixed = TRUE)
stopifnot(length(j) == 1, trimws(src[j + 1]) == "by = 1:nrow(LWSelf)]")
src[j] <- sub("min(amount/amount_live, amount/amount_work)), ", "pmin(amount/amount_live, amount/amount_work))]",
              src[j], fixed = TRUE)
fast <- eval(parse(text = src[-(j + 1)]))
environment(fast) <- ns
assignInNamespace("getLeastSelfContained", fast, ns = "LabourMarketAreas")
a <- commandArgs(trailingOnly = TRUE)
stopifnot(length(a) >= 6)
verbose <- length(a) >= 7 && a[7] == "verbose"
od <- fread(a[1], colClasses = c(origin = "character", dest = "character", flow = "numeric"))
codes <- sort(unique(c(od$origin, od$dest)))
id <- setNames(seq_along(codes), codes)
lw <- data.table(community_live = as.integer(id[od$origin]),
                 community_work = as.integer(id[od$dest]),
                 amount = od$flow)
t0 <- Sys.time()
res <- findClusters(LWCom = lw, minSZ = as.numeric(a[3]), minSC = as.numeric(a[4]),
                    tarSZ = as.numeric(a[5]), tarSC = as.numeric(a[6]), verbose = verbose)
secs <- as.numeric(difftime(Sys.time(), t0, units = "secs"))
cl <- res$lma$clusterList
out <- data.table(unit = codes[cl$community], area = paste0("LMA", cl$cluster), residents = cl$residents)
fwrite(out, a[2])
run <- data.table(units = nrow(out), areas = uniqueN(out$area), seconds = round(secs),
                  package = paste("LabourMarketAreas", as.character(packageVersion("LabourMarketAreas"))),
                  r = R.version.string)
fwrite(run, sub("\\.csv$", "_run.csv", a[2]))
cat(sprintf("units %d areas %d seconds %.0f %s %s\n", run$units, run$areas, secs, run$package, run$r))
