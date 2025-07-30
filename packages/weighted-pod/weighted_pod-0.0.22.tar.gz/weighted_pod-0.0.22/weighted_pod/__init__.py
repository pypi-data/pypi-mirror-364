"""
WeightedPOD: A library for Proper Orthogonal Decomposition with weighted inner products
for non-uniform mesh CFD results.

Author: Hakan
Created: July 24, 2025
"""

from .core import WeightedPOD
from .utils import read_files, parse_case_name, load_fluidfoam_data,load_data_Volume
from .visualization import plot_modes, plot_energy_spectrum, plot_reconstruction

__version__ = "0.0.21"
__author__ = "Muhammet Hakan Demir"
__email__ = "muhammet.demir@ruhr-uni-bochum.de"

__all__ = [
    'WeightedPOD',
    'read_files',
    'parse_case_name', 
    'load_fluidfoam_data',
    'load_data_Volume',
    'plot_modes',
    'plot_energy_spectrum',
    'plot_reconstruction'
]
