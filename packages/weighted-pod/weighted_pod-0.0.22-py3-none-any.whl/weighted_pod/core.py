#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 13:55:26 2025

@author: hakan

Core WeightedPOD implementation for CFD analysis with non-uniform mesh.

This module contains the main WeightedPOD class for computing POD modes
with volume-weighted inner products.
"""

import numpy as np 
import matplotlib.pyplot as plt
from scipy.linalg import svd, eigh 
import gc  # For memory management



class WeightedPOD:
    """
        Parameters:
        -----------
        data_matrix : numpy.ndarray
            Shape (N, M) where N is spatial points and M is number of snapshots
        volumes : numpy.ndarray
            Shape (N,) containing cell volumes for each spatial point
        mean_subtraction : bool
            Whether to subtract temporal mean (default: True)

       Attributes:
       -----------
        X : numpy.ndarray
          Input data matrix
        volumes : numpy.ndarray
          Cell volumes for weighting
        N : int
          Number of spatial points
        M : int
          Number of snapshots
        phi_pod : numpy.ndarray
            Spatial POD modes
        a_pod : numpy.ndarray
            Temporal coefficients
        lambda_pod : numpy.ndarray
            Eigenvalues (energy content)
        energy_content : numpy.ndarray
            Energy percentage of each mode
        cumulative_energy : numpy.ndarray
            Cumulative energy percentage
            
    """
    
    def __init__(self, data_matrix, volumes, mean_subtraction=True):
        # you have to convert to float32 to save memory 
        self.X = data_matrix.astype(np.float32)
        self.volumes = volumes.astype(np.float32)
        self.mean_subtraction = mean_subtraction
        self.N, self.M = self.X.shape  # N = spatial points, M = snapshots
        
        print(f"Initializing POD with {self.N:,} spatial points and {self.M} snapshots")
      #  print(f"Data memory usage: ~{(self.X.nbytes / 1e9):.2f} GB")
      #  print(f"Volume memory usage: ~{(self.volumes.nbytes / 1e6):.1f} MB")  
        
        # Subtract mean if requested
        if self.mean_subtraction:
            print("Computing and subtracting mean...")
            self.X_mean = np.mean(self.X, axis=1, keepdims=True)
            self.X_centered = self.X - self.X_mean
        else:
            self.X_mean = np.zeros((self.N, 1), dtype=np.float32)
            self.X_centered = self.X.copy()

    def compute_pod_method_of_snapshots(self):
        print(f"\nComputing POD using method of snapshots...")
        print(f"Data shape: {self.X.shape}")
        print(f"Volume weights shape: {self.volumes.shape}")
        
        sqrt_volumes = np.sqrt(self.volumes)
        
        # Apply weights element-wise (no large matrix creation)
        
        # X_centered (N,M) , sqrt_volumes(N,1) , X_weighted (N,M)
        X_weighted = self.X_centered * sqrt_volumes[:, np.newaxis]
        # Correlation Matrix , C = X.T @ W @ X -- for snapshot method  
        C = X_weighted.T @ X_weighted  # Shape: (M, M) 

        # Clean up weighted matrix to save memory
        del X_weighted
        gc.collect()

        # Eigendecomposition of square matrix (M,M)
        eigenvals, eigenvecs = eigh(C)
        # Sort in descending order
        idx = np.argsort(eigenvals)[::-1]
        eigenvals = eigenvals[idx]
        eigenvecs = eigenvecs[:, idx]
        
        # Filter out numerical zeros
        positive_mask = eigenvals > 1e-12
        eigenvals = eigenvals[positive_mask]
        eigenvecs = eigenvecs[:, positive_mask]
        n_modes = len(eigenvals)
        
        print(f"Found {n_modes} positive eigenvalues out of {self.M}")
        
        # Compute spatial POD modes
        print("Computing spatial POD modes and coefficients...")
        self.lambda_pod = eigenvals
        self.phi_pod = np.zeros((self.N, n_modes), dtype=np.float32)
        
        for i in range(n_modes):
            if i % 5 == 0:
                print(f"  Computing mode {i+1}/{n_modes}...")
           
            # modes = X_centered @ eigenvectors / sqrt(eigenvalue) (this is the standard approach)
            # reference:  Modal Analysis of Fluid Flows: An Overview

            # Compute spatial mode
            self.phi_pod[:, i] = self.X_centered @ eigenvecs[:, i] / np.sqrt(eigenvals[i])  
            
            # this is verification 
            weighted_norm_squared = np.sum(self.volumes * self.phi_pod[:, i]**2)
            
            if i < 3:  # Check first few modes
              print(f"    Mode {i+1} weighted norm²: {weighted_norm_squared:.6f}")
    
        
        # Compute temporal coefficients using weighted inner product
        print("Computing temporal coefficients...")
        # vectorized  
        # A = phi^T @ diag(volumes) @ X_centered
        weighted_phi = self.phi_pod * self.volumes[:, np.newaxis]  # Apply weights
        self.a_pod = weighted_phi.T @ self.X_centered
    



        # Energy content analysis
        total_energy = np.sum(eigenvals)
        self.energy_content = eigenvals / total_energy * 100
        self.cumulative_energy = np.cumsum(self.energy_content)
        
        print(f"\nPOD computation completed successfully!")
        print(f"First mode captures {self.energy_content[0]:.2f}% of total energy")
        print(f"First 3 modes capture {self.cumulative_energy[2]:.2f}% of total energy")
        
        return self.phi_pod, self.a_pod, self.lambda_pod

    def compute_pod_svd(self):
        """
        Compute POD using SVD approach.
        
        Returns:
        --------
        tuple
            (phi_pod_svd, a_pod_svd, lambda_pod_svd) - spatial modes, temporal coefficients, eigenvalues
        """

        print("Computing POD using SVD approach...")
        # Apply weights element-wise
        sqrt_volumes = np.sqrt(self.volumes)
        X_weighted = self.X_centered * sqrt_volumes[:, np.newaxis]
        # SVD decomposition
        print("Performing SVD...")
        U, sigma, VT = svd(X_weighted, full_matrices=False)
        
                
        # Remove weight scaling element-wise
        self.phi_pod_svd = U / sqrt_volumes[:, np.newaxis]
        self.a_pod_svd = sigma[:, np.newaxis] * VT
        self.lambda_pod_svd = sigma**2
        
        # Clean up
        del X_weighted
        gc.collect()
        
        return self.phi_pod_svd, self.a_pod_svd, self.lambda_pod_svd
    
    
    def reconstruct_field(self, n_modes, snapshot_idx=None):
        """
        Reconstruct flow field using first n_modes.
        
        Parameters:
        -----------
        n_modes : int
            Number of modes to use for reconstruction
        snapshot_idx : int, optional
            Index of specific snapshot to reconstruct. If None, reconstructs all.
            
        Returns:
        --------
        numpy.ndarray
            Reconstructed field(s)
        """


        if not hasattr(self, 'phi_pod'):
            raise ValueError("POD not computed yet. Run compute_pod_method_of_snapshots() first.")
        
        n_modes = min(n_modes, self.phi_pod.shape[1])
        
        if snapshot_idx is not None:
            # Reconstruct single snapshot
            reconstructed = self.X_mean.flatten() + \
                          np.sum([self.a_pod[i, snapshot_idx] * self.phi_pod[:, i] 
                                 for i in range(n_modes)], axis=0)
            return reconstructed
        else:
            # Reconstruct all snapshots
            reconstructed = self.X_mean + \
                           self.phi_pod[:, :n_modes] @ self.a_pod[:n_modes, :]
            return reconstructed
