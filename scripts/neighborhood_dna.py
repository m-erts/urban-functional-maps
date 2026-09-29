"""Functional mix per H3 cell from Overture Maps Places, read straight from S3.

    python scripts/neighborhood_dna.py 34.30 132.35 34.48 132.55 hiroshima
    python scripts/neighborhood_dna.py 44.72 20.35 44.87 20.55 belgrade --release 2026-08-19.0

Arguments: lat_min lon_min lat_max lon_max name. Output: <name>_dna.parquet, one row per cell
with at least MIN_POI places: counts, Shannon entropy, Hill numbers q1 and q2, top-category share.
Overture keeps a release on S3 for about two months; archive the output if you need it later.
"""

import argparse
import sys

import duckdb

H3_RES, LEVEL, MIN_POI = 8, 1, 10  # cell size, taxonomy depth (1 = 13 branches), minimum sample

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("bbox", nargs=4, type=float, metavar=("LAT_MIN", "LON_MIN", "LAT_MAX", "LON_MAX"))
ap.add_argument("name")
ap.add_argument("--release", default="2026-08-19.0")
a = ap.parse_args()
ymin, xmin, ymax, xmax = a.bbox
if not (ymin < ymax and xmin < xmax):
    sys.exit("bbox must be lat_min lon_min lat_max lon_max with min < max")

src = f"s3://overturemaps-us-west-2/release/{a.release}/theme=places/type=place/*"
con = duckdb.connect()
try:
    con.sql("INSTALL httpfs; LOAD httpfs; INSTALL h3 FROM community; LOAD h3; SET s3_region='us-west-2';")
    if not con.sql(f"SELECT count(*) FROM glob('{src}')").fetchone()[0]:
        sys.exit(f"release {a.release} is not on S3 any more; list current ones at docs.overturemaps.org")
    con.sql(f"""
    CREATE TABLE cells AS
    WITH places AS (
        SELECT h3_latlng_to_cell(bbox.ymin, bbox.xmin, {H3_RES}) AS cell,
               taxonomy.hierarchy[least({LEVEL}, len(taxonomy.hierarchy))] AS category
        FROM read_parquet('{src}', hive_partitioning = 1)
        WHERE bbox.xmin BETWEEN {xmin} AND {xmax} AND bbox.ymin BETWEEN {ymin} AND {ymax}
          AND taxonomy IS NOT NULL AND len(taxonomy.hierarchy) > 0),
    shares AS (
        SELECT cell, category, n, n / sum(n) OVER (PARTITION BY cell) AS p
        FROM (SELECT cell, category, count(*)::DOUBLE AS n FROM places GROUP BY 1, 2))
    SELECT cell, h3_cell_to_boundary_wkt(cell) AS geometry, sum(n) AS poi_count,
           count(*) AS cat_richness, -sum(p * ln(p)) AS cat_shannon,
           -sum(p * ln(p)) / nullif(ln(count(*)), 0) AS cat_evenness,
           exp(-sum(p * ln(p))) AS cat_hill_q1, 1 / sum(p * p) AS cat_hill_q2,
           max(p) AS top_cat_share, arg_max(category, p) AS dominant_category
    FROM shares GROUP BY cell HAVING sum(n) >= {MIN_POI}""")
    con.sql(f"COPY cells TO '{a.name}_dna.parquet' (FORMAT parquet)")
except duckdb.Error as e:
    sys.exit(f"DuckDB could not read Overture ({type(e).__name__}): {e}")

print(
    con.sql("""SELECT count(*) AS cells, sum(poi_count)::INT AS places,
    round(median(cat_hill_q1), 2) AS median_hill_q1, round(median(cat_hill_q2), 2) AS median_hill_q2,
    round(median(top_cat_share), 2) AS median_top_share,
    count(*) FILTER (top_cat_share >= 0.5) AS cells_one_function_holds_half FROM cells""")
    .df()
    .to_string(index=False)
)
