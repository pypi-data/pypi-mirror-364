"""
Utilities to perform the generalized random tessellation sampling
"""

import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon

from .utils import set_rng


def _build_grid_first(gdf):
    geoms = []
    v = np.arange(4)
    np.random.shuffle(v)
    xmin = gdf.bounds.minx.min()
    xmax = gdf.bounds.maxx.max()
    ymin = gdf.bounds.miny.min()
    ymax = gdf.bounds.maxy.max()
    n = 3
    lstx = np.linspace(xmin, xmax, n)
    lsty = np.linspace(ymin, ymax, n)
    for kx in range(n - 1):
        for ky in range(n - 1):
            xmin = lstx[kx]
            xmax = lstx[kx + 1]
            ymin = lsty[ky]
            ymax = lsty[ky + 1]
            x_point_list = [xmax, xmin, xmin, xmax]
            y_point_list = [ymax, ymax, ymin, ymin]
            polygon_geom = Polygon(zip(x_point_list, y_point_list))
            geoms.append(polygon_geom)
    gdf_poly = gpd.GeoDataFrame(
        index=range(len(geoms)),
        data={"label": [str(elem) for elem in v]},
        crs=gdf.crs,
        geometry=geoms,
    )
    return gdf_poly


def _build_grid_next_single(geom_bounds, label, crs, rng):
    geoms = []
    v = np.arange(4)
    rng.shuffle(v)
    xmin = geom_bounds.minx
    xmax = geom_bounds.maxx
    ymin = geom_bounds.miny
    ymax = geom_bounds.maxy
    n = 3
    lstx = np.linspace(xmin, xmax, n)
    lsty = np.linspace(ymin, ymax, n)
    for kx in range(n - 1):
        for ky in range(n - 1):
            xmin = lstx[kx]
            xmax = lstx[kx + 1]
            ymin = lsty[ky]
            ymax = lsty[ky + 1]
            x_point_list = [xmax, xmin, xmin, xmax]
            y_point_list = [ymax, ymax, ymin, ymin]
            polygon_geom = Polygon(zip(x_point_list, y_point_list))
            geoms.append(polygon_geom)
    gdf_poly = gpd.GeoDataFrame(
        index=range(len(geoms)),
        data={"label": [label + str(elem) for elem in v]},
        crs=crs,
        geometry=geoms,
    )
    return gdf_poly


def _build_grid_next(gdf, rng):
    out = []
    for j in range(len(gdf)):
        geom_bounds = gdf["geometry"].bounds.iloc[j]
        label = gdf["label"].iloc[j]
        out.append(_build_grid_next_single(geom_bounds, label, gdf.crs, rng=rng))
    return pd.concat(out)


def _verify_stop(gdf, gdf_poly):
    if len(gdf_poly) < len(gdf):
        return 0
    # Each cell must have at most 1 point inside
    cond = (
        gdf.sjoin(gdf_poly, how="right", predicate="within")
        .groupby("label")
        .count()["geometry"]
        .max()
        == 1
    )
    if not cond:
        return 0
    return 1


def sample_generalized_random_tessellation(
    gdf: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    n: int,
    proba: np.array = None,
    rng: np.random.Generator = None,
):
    """
    Performs a GRT sampling, as described in https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://www.jstatsoft.org/article/view/v105i03/4407&ved=2ahUKEwj6wJbT7M-OAxWZ7rsIHQ2fEFUQFnoECCwQAQ&usg=AOvVaw1qitmi60ji1YVo0nXhXrB9
    :param gdf: the geodataframe containing the population
    :param gdf_bounds: a geodataframe used to define the boundaries of the grid
    :param n: the number of points to sample
    :param proba: optional array containing the inclusion probability of each location
    :param rng: optional random number generator
    :return: np.array the
    """
    rng = set_rng(rng)
    if proba is None:
        proba = np.ones(len(gdf)) / len(gdf) * n
    else:
        proba /= np.sum(proba)
        proba *= n
    gdf_poly = _build_grid_first(gdf_bounds)
    cond = _verify_stop(gdf, gdf_poly)
    if not cond:
        while not cond:
            gdf_poly = _build_grid_next(gdf_poly, rng=rng)
            cond = _verify_stop(gdf, gdf_poly)
    gdf_out = gdf.sjoin(gdf_poly, how="left", predicate="within")
    gdf_out["proba"] = proba
    gdf_out["label"] = gdf_out["label"].str[::-1].astype(int)
    gdf_out.sort_values(by="label", inplace=True)
    gdf_out["proba_cumsum"] = np.cumsum(gdf_out["proba"])
    gdf_out["idx"] = gdf_out.index
    gdf_out["id"] = np.arange(len(gdf_out))
    gdf_out.set_index("id", inplace=True)
    v0 = rng.uniform()
    rnd = v0 + np.arange(n)
    idx = [gdf_out[gdf_out["proba_cumsum"] < v0].index[-1] for v0 in rnd]
    msk = gdf_out.index.isin(idx)
    idv = gdf_out[msk]["idx"]
    msk = gdf.index.isin(idv)
    return msk
