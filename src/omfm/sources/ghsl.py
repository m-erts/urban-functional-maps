"""Degree of urbanisation per polygon from GHS-SMOD classes weighted by GHS-POP population.

Weight by population, not by area. Urban classes cover a tiny share of land: in Serbia the
area-weighted urban share is zero for a large part of the municipalities, and correlations
computed on it are correlations with noise.
"""

from __future__ import annotations

import numpy as np

from ..config import params, path

__all__ = ["urbanisation"]


def _tif_in_zip(rel: str) -> str:
    import zipfile

    z = path("raw", rel)
    with zipfile.ZipFile(z) as zf:
        member = next(n for n in zf.namelist() if n.endswith(".tif"))
    return f"/vsizip/{z}/{member}"


def urbanisation(gdf):
    """Return ``gdf`` (any CRS) with population- and area-weighted urban shares.

    Adds: pop_ghsl, deg_urb (population share in urban classes), deg_city (population share in
    urban centres), area_urb (pixel share in urban classes), clipped (polygon reaches beyond
    the raster tile, so its totals are incomplete).
    """
    import rasterio
    from rasterio.features import rasterize
    from rasterio.warp import Resampling, reproject
    from rasterio.windows import from_bounds

    cfg = params()["serbia"]["ghsl"]
    g = gdf.to_crs("ESRI:54009").reset_index(drop=True)
    with rasterio.open(_tif_in_zip(cfg["pop"])) as rp:
        b = g.total_bounds
        x0, y0 = max(b[0] - 500, rp.bounds.left), max(b[1] - 500, rp.bounds.bottom)
        x1, y1 = min(b[2] + 500, rp.bounds.right), min(b[3] + 500, rp.bounds.top)
        win = from_bounds(x0, y0, x1, y1, rp.transform)
        pop = rp.read(1, window=win).astype("float32")
        tr = rp.window_transform(win)
        y_bottom = rp.bounds.bottom
    pop[pop < 0] = 0
    with rasterio.open(_tif_in_zip(cfg["smod"])) as rs:
        smod = np.zeros(pop.shape, dtype="int16")
        reproject(
            source=rasterio.band(rs, 1),
            destination=smod,
            dst_transform=tr,
            dst_crs="ESRI:54009",
            resampling=Resampling.nearest,
        )
    zones = rasterize(
        [(geom, i + 1) for i, geom in enumerate(g.geometry)], out_shape=pop.shape, transform=tr, fill=0, dtype="int32"
    )
    urb, city = np.isin(smod, cfg["urban_classes"]), np.isin(smod, cfg["city_classes"])
    n, z = len(g) + 1, zones.ravel()
    tot = np.bincount(z, weights=pop.ravel(), minlength=n)[1:]
    p_urb = np.bincount(z, weights=(pop * urb).ravel(), minlength=n)[1:]
    p_city = np.bincount(z, weights=(pop * city).ravel(), minlength=n)[1:]
    px = np.bincount(z, minlength=n)[1:]
    px_urb = np.bincount(z, weights=urb.ravel().astype(float), minlength=n)[1:]
    out = gdf.reset_index(drop=True).copy()
    with np.errstate(divide="ignore", invalid="ignore"):
        out["pop_ghsl"] = tot
        out["deg_urb"] = np.where(tot > 0, p_urb / tot, np.nan)
        out["deg_city"] = np.where(tot > 0, p_city / tot, np.nan)
        out["area_urb"] = np.where(px > 0, px_urb / px, np.nan)
    out["clipped"] = (g.geometry.bounds.miny < y_bottom).to_numpy()
    return out
