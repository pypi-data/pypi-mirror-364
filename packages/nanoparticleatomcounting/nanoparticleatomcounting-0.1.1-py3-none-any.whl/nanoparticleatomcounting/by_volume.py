"""
Volume-based routines for estimating atom counts in supported nanoparticles.

Functions
---------
calculate_volumes(element: str, r: float, theta: float, facet: tuple) -> tuple
    Calculate volume of the interfacial region (excluding the perimeter region),
    perimeter region, and the entire nanoparticle
    using:
        1. contact angle (theta)
        2. footprint/interfacial radius (r) in Angstrom
        3. chemical symbol of the nanoparticle's atoms (element)
        4. facet of nanoparticle oriented to support (facet)

calculate_by_volume(element: str, r: float, theta: float, facet: tuple) -> tuple
    Main function to do all calculations through the 'volume' method
"""
from typing import Tuple, List
import numpy as np
import warnings
from nanoparticleatomcounting.count_utilities import (
        volume_to_atoms,
        area_to_atoms,
        calculate_atomic_density,
        calculate_total_volume,
        calculate_surface_area,
        calculate_constants
        )

#warnings.filterwarnings(action="ignore")

def calculate_volumes(
        element: str,
        footprint_radius: float,
        theta: float = None,
        facet: Tuple[int,int,int] = None
        ) -> Tuple[float, float, float]:
    """
    Calculate volume of the interfacial region (excluding the perimeter region),
    perimeter region, and the entire nanoparticle

    Requires:
        element (str):              atomic symbol for atom type in the nanoparticle
        theta (float):              contact angle. degrees
        footprint_radius (float):   NP footprint radius. In Ang
        facet (Tuple[int,int,int]): facet facing the support

    Returns:
        interface_volume, perimeter_volume, total_volume     all in A^3
    """
    #R: radius from spherical cap center,
    #r: footprint radius (i.e. radius of bottom of spherical segment),
    #x: radius of top of spherical segment, z: height of spherical segment,
    #x2: x but excluding the perimeter having thickness == z,
    #r2: r but excluding the perimeter having thickness == z,
    #h:
        #if θ>90: distance from sphere center vertically down to top of spherical segment
        #if θ<90: distance from sphere center vertically up to bottom of spherical segment
        #if θ==90: zero
    #z1: atomic diameter
    #z: interplanar spacing (height of the interface)
    _, z, z1 = calculate_constants(element = element, facet = tuple(facet))

    r = footprint_radius
    R = r / np.sin(np.radians(theta))
    #r2 = radial spacing
    r2 = np.clip(r - z1, 0, None) #no reliable formula for radial spacing. assumed to be = atomic diameter
                                  #clip so it doesn't become negative for extremely small footprint radii
    ##Find h and x
    if theta > 90:
        h = np.sqrt(R**2 - r**2) - z #thus spake pythagoras
        x = np.sqrt(R**2 - h**2) #eqn 1
        dome_height = h + z + R
        x2 = np.sqrt((2*h*z) - (z**2) + (r2**2)) #from eqn1, noting that R^2 = (h+z)^2 + r^2 and then substituting r2 for r
    else:
        h = np.clip(np.sqrt(R**2 - r**2), 0, None) #clip so h==0 if theta == 90
        dome_height = R + h
        x = np.sqrt(R**2 - ((h + z)**2)) #eqn 2
        x2 = np.sqrt((h**2) - ((h+z)**2) + (r2**2)) #can have invalid values; see below notes

#    print(f"Central radius: {R} A")
#    print(f"Height of dome: {dome_height} A")
#    print(f"Interface height: {z} A")
#    print(f"Radius of spherical segment: {x} A")
#    print(f"Footprint radius: {r} A")

    #Formula from https://en.wikipedia.org/wiki/Spherical_segment
    segment_volume = np.pi * z * ((3 * (r**2 + x**2)) + z**2) / 6
    interface_volume = np.pi * z * ((3 * (r2**2 + x2**2)) + z**2) / 6
    total_volume = calculate_total_volume(r, theta)

    #if x2 was negative, then it means for the given combination of r and theta, if you shave off z from r
    #then too much will be shaved off from the top of the spherical segment that its radius (x2) becomes negative
    #this implies that we can't have any non-perimeter atoms for such a system
    #for a given r, will be more likely for smaller theta
    #for a given theta, will be more likely for smaller r
    if np.isnan(interface_volume):
        warnings.warn(
        f"""footprint radius ({r}) and-or θ ({theta}) too small.
        There is no non-perimeter for the given combination of r and θ""",
        category = RuntimeWarning
        )
        interface_volume = 0

    perimeter_volume = segment_volume - interface_volume

    return interface_volume, perimeter_volume, total_volume


def calculate_by_volume(
        element: str,
        footprint_radius: float,
        theta: float = None,
        facet: Tuple[int,int,int] = None
        ) -> Tuple[int, int, int, int]:
    """
    Main function to do all calculations through the 'volume' method

    Units: A^3

    Requires:
        element (str):              atomic symbol for atom type in the nanoparticle
        theta (float):              contact angle. degrees
        footprint_radius (float):   NP footprint radius. In Ang
        facet (Tuple[int,int,int]): facet facing the support
                                    for defaults, see the calculate_constants() function

    Returns:
        perimeter_atoms, interfacial_atoms, surface_atoms, all_atoms
    """

    interfacial_volume, perimeter_volume, total_volume = calculate_volumes(
            element = element,
            footprint_radius = footprint_radius,
            theta = theta,
            facet = facet
            )

    interfacial_atoms, perimeter_atoms, total_atoms = [
            volume_to_atoms(
        volume = i,
        element = element,
        molar_volume = None,
        facet = facet
        ) for i in [
            interfacial_volume,
            perimeter_volume,
            total_volume
            ]
            ]

    surface_area = calculate_surface_area(
            element = element,
            footprint_radius = footprint_radius,
            theta = theta,
            facet = facet
            )

    surface_atoms = area_to_atoms(
            area = surface_area,
            element = element,
            facet = facet
            )

    return perimeter_atoms, interfacial_atoms, surface_atoms, total_atoms


