# Roadmap

## Done in version 1.0.0

- England and Wales 2011 and 2021: matrices with the code list applied, delimitation, contiguity repair, permutation null with closed form, validity rule with two naive repairs, agreement with the official areas, iso-count experiment, six cases of boundary divergence.
- The Coombes-Bond algorithm (R package LabourMarketAreas 3.4) with the parameters of the official areas, on England and Wales 2011, the Netherlands 2023 and Spain 2023.
- A recombination Markov chain on spanning trees for contiguous partitions of the same sizes; decomposition of self-containment into scale, contiguity and placement for ten partitions in three countries; convergence diagnostics. Region growing is kept for comparison.
- Netherlands 2023: municipal pairs of table 85481NED, delimitation, test of the 40 COROP regions. Netherlands 2014: self-containment of the 40 regions.
- Spain 2023: five weekdays of trips between districts, home to work or study, hourly profile, delimitation.
- Serbia 2022: band self-containment for work and education, one-to-one join to polygons, urbanisation by population and by area.
- Japan 2019 to 2021: day and night, local share, normalisation check, signatures, clusterability.
- OpenStreetMap traces: sample size and concentration. The comparison with places and with presence is computed but not reported (eleven shared cells).
- Register of the numbers of deck v1; errata; paper; slides; response to reviewers.

## Next, in order of what they would add

1. Coombes-Bond on the 2021 matrix, and on the Dutch series 2021 to 2024, to see whether changes between years exceed the change from rounding.
2. The contiguity fine-tuning of LabourMarketAreas in the decomposition, beside the raw output.
3. The Spanish matrix of recurrent mandatory mobility, which counts persons, in place of trips.
4. Several starting partitions per chain, and other ensembles of contiguous partitions.
5. Japanese census commuting pairs for Hiroshima.
6. GHSL epoch 2020 in place of the 2030 projection.
7. District-level adjacency, so that the contiguous null can be run at both scales.
8. GeoPackage of all layers with a QGIS project.
