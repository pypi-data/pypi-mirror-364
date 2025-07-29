import numpy as np

from scipy.spatial import KDTree

from typing import Literal, overload
from annotated_types import Annotated, Union, Ge

# import pandas as pd
# import astropy.units as u


@overload
def close_distance(
    iso_positions: np.ndarray,
    gmc_positions: np.ndarray,
    timesteps: Annotated[int, Ge(1)],
    include_gmcs: Literal[True] = True,
    num_distances: Annotated[int, Ge(1)] = 1,
    upper_bound: Annotated[float, Ge(1)] = 1,
    multiprocessing: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    pass


@overload
def close_distance(
    iso_positions: np.ndarray,
    gmc_positions: np.ndarray,
    timesteps: Annotated[int, Ge(1)],
    include_gmcs: Literal[False],
    num_distances: Annotated[int, Ge(1)] = 1,
    upper_bound: Annotated[float, Ge(1)] = 1,
    multiprocessing: bool = True,
) -> np.ndarray:
    pass


def close_distance(
    iso_positions: np.ndarray,
    gmc_positions: np.ndarray,
    timesteps: Annotated[int, Ge(1)],
    include_gmcs: bool = False,
    num_distances: Annotated[int, Ge(1)] = 1,
    upper_bound: Annotated[float, Ge(1)] = 1,
    multiprocessing: bool = True,
) -> Union[tuple[np.ndarray, np.ndarray], np.ndarray]:
    """
    :param iso_positions:
    :param gmc_positions:
    """
    if iso_positions.shape[1] != 3:
        raise Exception("Did not provide iso position list with shape (,3)")
    if gmc_positions.shape[1] != 3:
        raise Exception("Did not provide gmc position list with shape (,3)")
    dds = list()
    iis = list()
    ips = np.split(iso_positions, timesteps, axis=0)
    gps = np.split(gmc_positions, timesteps, axis=0)
    for ip, gp in zip(ips, gps):
        tree = KDTree(gp)
        dd, ii = tree.query(
            ip,
            num_distances,
            distance_upper_bound=upper_bound,
            workers=-1 if multiprocessing else 1,
        )
        dds.extend(dd)
        iis.extend(ii)
    if include_gmcs:
        return np.array(dds), np.array(iis)
    else:
        return np.array(dds)


def close_passage(
    distances: np.ndarray,
    cutoff: float,
    output: Literal["percentage", "counts"] = "percentage",
):
    """
    :param distances:
    :param cutoff:
    :param output:
    """
    res = distances[distances < cutoff]
    match output:
        case "percentage":
            len(res) / len(distances)
        case "counts":
            len(res)
