"""
Utilities that the atom counting routines rely on

Functions
---------
calculate_constants:
    Extract molar volume (assumed at equilibrium),
    interplanar spacing, and atomic diameter
calculate_surface_area:
    Calculate area of outer surface of NP
    Excludes the interfacial area and the side area of the perimeter
volume_to_atoms:
    Convert volume (in A^3) to number of atoms
area_to_atoms:
    Convert area (in A^2) to number of atoms
calculate_atomic_density:
    Calculate atomic density (i.e. atoms per unit surface area)
calculate_total_volume:
    Calculate Nanoparticle volume, ASSUMING IT'S A SPHERICAL CAP
alpha:
    a constant needed in the spherical cap equations
beta:
    a constant needed in the spherical cap equations
"""
from typing import Tuple, List
from sys import argv, exit
import numpy as np
import warnings
from functools import lru_cache
from nanoparticleatomcounting.data import (
        chemical_symbols,
        atomic_numbers,
        atomic_names,
        covalent_radii,
        reference_states,
        molar_volumes,
        interplanar_dist,
        N_A
        )

##extracts molar volume, interplanar spacing, and diameter of the nanoparticle element
DEFAULT_FACETS = {
        "fcc": "(1, 1, 1)",
        "bcc": "(1, 1, 0)",
        "sc": "(1, 0, 0)",
        "orthorhombic": "(1, 1, 1)",
        "hcp": "(0, 0, 1)",
        "rhombohedral": "(1, 1, 1)",
        "bct": "(1, 1, 1)",
        } #confirmed these to generally be the lowest-energy facets
          #(https://next-gen.materialsproject.org/materials and http://crystalium.materialsvirtuallab.org/)

warnings.filterwarnings("ignore")

@lru_cache(maxsize = 10_000)
def calculate_constants(
        element: str,
        facet: Tuple[int, int, int] = None
        ) -> float:
    f"""
    Extract molar volume (assumed at equilibrium),
    interplanar spacing, and atomic diameter

    Requires:
        element (str):      atomic symbol for atom type in the nanoparticle
        facet (Tuple[int,int,int]):
                            facet facing the support.
                            Defaults: {DEFAULT_FACETS}

    Returns:
        molar volume (float) in A^3/mole,
        interplanar spacing (d) in A
        covalent diameter in A

    Exceptions:
        ValueError if crystal system of the nanoparticle's element is not supported
    """
    ##in case facet is given as (x,y,z) rather than (x, y, z) as expected in data.py
    h, k, l = facet if facet else [None] * 3
    facet = f"({h}, {k}, {l})"
#    print(facet, element)

    if facet == "(0, 0, 0)":
        raise ValueError(f"Facet cannot be {facet}")

#    if facet is not None and not isinstance(facet, tuple):
#        facet = tuple(facet)

    element = element.capitalize()

    try:
        atomic_number = atomic_numbers[element]
        #if facet not given, pick default
        if h is None:
            reference_state = reference_states[atomic_number]
            crystal_lattice = reference_state["symmetry"]
            facet = DEFAULT_FACETS[crystal_lattice]
            warnings.warn(
                    f"Interfacial facet not given, will assume {facet}",
                    category = UserWarning
                    )
        covalent_radius = covalent_radii[atomic_number]
        molar_volume = molar_volumes[element]
        interplanar_distance = interplanar_dist[element][facet]
    except KeyError:
        raise KeyError(f"Element type {element} not supported!")
    except Exception as unknown_:
        print(f"Unexpected error occured:\t{unknown_}")

    return molar_volume, interplanar_distance, 2 * covalent_radius


def alpha(theta: int) -> float:
    """
    Constant needed for the spherical cap model equations.
    theta is in degrees
    """
    return 1 / (1 + np.cos(np.radians(theta)))


def beta(theta: int) -> float:
    """
    Constant needed for the spherical cap model equations.
    theta is in degrees
    Will give infinity if theta = 0 or 180
    """
    if theta in [0, 180]:
        raise ValueError(f"Contact angle of {theta} not allowed")

    return (2 + np.cos(np.radians(theta))) *\
            (1 - np.cos(np.radians(theta))) / (np.sin(np.radians(theta)))


def calculate_surface_area(
        element: str,
        footprint_radius: float,
        theta: float = None,
        facet: Tuple[int,int,int] = None
        ) -> float:
    """
    Calculate area of outer surface of NP
    Excludes the interfacial area and the side area of the perimeter

    Requires:
        element (str):              atomic symbol for atom type in the nanoparticle
        facet (Tuple[int,int,int]): facet facing the support.
                                    see calculate_constants() for defaults
        theta (float):              contact angle. degrees

    Returns:
        surface area (float) in A^2
    """
    if theta in [0, 180]:
        raise ValueError(f"Contact angle of {theta} not allowed")

    r = footprint_radius #to make things clear
    _, interplanar_spacing, _ = calculate_constants(element, facet)
    z = interplanar_spacing #to make things clear

    theta_rad = np.radians(theta)
    #how theta changes with shaving off interfacial height
    arg = np.clip(np.cos(theta_rad) + ((z/r) * np.sin(theta_rad)), -1.0, 1.0)
#    if arg > 1.0:
#        warnings.warn(f"""ratio of interplanar spacing and footprint radius too large: ({z/r});
#        no real cap angle can exist after shaving interface.""",
#        category = RuntimeWarning)
#        arg = 1.0
    theta = np.degrees(np.arccos(arg))
    total_area = 2 * np.pi * (r**2) * alpha(theta)

    return total_area #A^2


def calculate_total_volume(
        footprint_radius: float,
        theta: float = None
        ) -> float:
    """
    Calculate Nanoparticle volume, ASSUMING IT'S A SPHERICAL CAP
    Units: A^3

    Requires:
        footprint_radius (float):   NP footprint radius. Ang
        theta (float):              contact angle. degrees

    Returns:
        volume (float):             NP volume. Ang^3
    """
    if theta in [0, 180]:
        raise ValueError(f"Contact angle of {theta} not allowed")
    if footprint_radius <= 10:
        warnings.warn(
        f"""A spherical cap may not work well for this footprint radius({footprint_radius})!
                Mind!""",
                category = UserWarning
                )
        
    return (np.pi * (footprint_radius ** 3)) * alpha(theta) * beta(theta) / 3


def calculate_atomic_density(
        element: str,
        facet: Tuple[int,int,int] = None
        ) -> float:
    """
    Calculate atomic density (i.e. atoms per unit surface area)

    Requires:
        element (str):              atomic symbol for atom type in the nanoparticle
        facet (Tuple[int,int,int]): facet facing the support.
                                    see calculate_constants() for defaults

    Returns:
        atomic density (float) in atoms/A^2
    """
    molar_volume, interplanar_spacing, _ = calculate_constants(element, facet)
    atomic_density = interplanar_spacing * N_A / molar_volume

    return atomic_density #atoms/A^2


def area_to_atoms(
        area: float,
        element: str,
        facet: Tuple[int,int,int] = None
        ) -> int:
    """
    Convert area (in A^2) to number of atoms

    Requires:
        area (float):               Area of region in A^2
        element (str):              atomic symbol for atom type in the nanoparticle
        facet (Tuple[int,int,int]): facet facing the support.
                                    see calculate_constants() for defaults

    Returns:
        N_atoms (int):      Number of atoms in region, rounded to nearest integer
    """
    atomic_density = calculate_atomic_density(element, facet) #atoms/A^2
    return int(area * atomic_density)


def volume_to_atoms(
        volume: float,
        element: str,
        molar_volume: float = None, 
        facet: Tuple[int, int, int] = None
        ) -> int:
    """
    Convert volume (in A^3) to number of atoms

    Requires:
        volume (float):             Volume of enclosed region in A^3
        element (str):              atomic symbol for atom type in the nanoparticle
        molar_volume (float):       molar volume in A^3/mole

    Returns:
        N_atoms (int):              Number of atoms in region, rounded to nearest integer
    """
    if not molar_volume:
        molar_volume, *_ = calculate_constants(element, facet)

    bulk_density = N_A / molar_volume #atom/A^3

    return np.round(volume * bulk_density)


