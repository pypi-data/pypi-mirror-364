"""
Area-based routines for estimating atom counts in supported nanoparticles.

Functions
---------
calculate_areas(element: str, r: float, theta: float, facet: tuple) -> tuple
    Calculate areas of the interface, perimeter, and surface
    using:
        1. contact angle (theta)
        2. footprint/interfacial radius (r) in Angstrom
        3. chemical symbol of the nanoparticle's atoms (element)
        4. facet of nanoparticle oriented to support (facet)

calculate_by_area(element: str, r: float, theta: float, facet: tuple) -> tuple
    Main function to do all calculations through the 'area' method
"""
from typing import Tuple, List
import numpy as np
import warnings
from nanoparticleatomcounting.count_utilities import (
        volume_to_atoms,
        calculate_total_volume,
        area_to_atoms,
        calculate_atomic_density,
        calculate_total_volume,
        calculate_surface_area,
        calculate_constants
        )


#calculate the number of interfacial atoms by looking only at the footprint radius, which means
#the contact angle doesn't affect the number of interfacial atoms
#should be fine for contact angles near 90 degrees
#if not, you may (or may not) want to calculate by volume instead

def calculate_areas(
        element: str,
        footprint_radius: float,
        theta: float = None,
        facet: Tuple[int,int,int] = None
        ) -> Tuple[float, float, float]:
    """
    Calculate area of:
        1. interface
        2. perimeter
        3. surface
            all in A^2

    Requires:
        element (str):              atomic symbol for atom type in the nanoparticle
        footprint_radius (float):   NP footprint radius. In Ang
        facet (Tuple[int,int,int]): facet facing the support
        theta (float):              contact angle, in degrees

    Returns:
        interfacial area (float):       interface area. excludes perimeter
        perimeter area (float):         perimeter area.
        surface area (float):           NP outer surface area. excludes interface
    """
    #r: footprint radius (i.e. radius of bottom of the interface),
    #inter_a: interfacial area (using the bottom of the interface).
            #this includes the area of the perimeter
    #peri_a: area of perimeter
    #inner_a: area of interface excluding the perimeter
    #surf_a: area of NP surface, excludes interfacial area
    #d:     atomic diameter
    #d: atomic diameter
    #z: interplanar spacing (height of the interface)
    _, z, d = calculate_constants(element, facet)

    r = footprint_radius
    footprint_a = np.pi * (r ** 2) #A^2
    interface_a = np.pi * ((r - d) ** 2) #A^2
    peri_a = footprint_a - interface_a #A^2
    surf_a = calculate_surface_area(element, r, theta, facet)

    return interface_a, peri_a, surf_a #all in A^2


def calculate_by_area(
        element: str,
        footprint_radius: float,
        theta: float = None,
        facet: Tuple[int,int,int] = None
        ) -> float:
    """
    Main function to do all calculations through the 'area' method

    Requires:
        element (str):              atomic symbol for atom type in the nanoparticle
        theta (float):              contact angle. degrees
        footprint_radius (float):   NP footprint radius. In Ang
        facet (Tuple[int,int,int]): facet facing the support
                                    for defaults, see the calculate_constants() function

    Returns:
        perimeter_atoms, interfacial_atoms, surface_atoms, all_atoms
    """
    interfacial_area, perimeter_area, NP_surface_area = calculate_areas(
            element,
            footprint_radius,
            theta,
            facet
            )

    perimeter_atoms, interfacial_atoms, NP_surface_atoms = [
            area_to_atoms(
                area = i,
                element = element,
                facet = facet
                ) for i in [
                    perimeter_area,
                    interfacial_area,
                    NP_surface_area
                    ]
            ]

    total_volume = calculate_total_volume(footprint_radius, theta)
    total_atoms = volume_to_atoms(total_volume, element, None, facet)

    return perimeter_atoms, interfacial_atoms, NP_surface_atoms, total_atoms



