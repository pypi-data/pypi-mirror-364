"""
WeightedPOD: A library for Proper Orthogonal Decomposition with weighted inner products
for non-uniform mesh CFD results.

Author: Hakan
Created: July 24, 2025
"""

from .core import WeightedPOD
from .utils import load_data, save_results, compute_reconstruction_error
from .visualization import plot_modes, plot_energy_spectrum, plot_reconstruction

__version__ = "0.0.1"
__author__ = "Muhammet Hakan Demir"
__email__ = "muhammet.demir@ruhr-uni-bochum.de"

__all__ = [
    'WeightedPOD',
    'load_data',
    'save_results', 
    'compute_reconstruction_error',
    'plot_modes',
    'plot_energy_spectrum',
    'plot_reconstruction'
]
