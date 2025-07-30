"""
Visualization functions for WeightedPOD results.
"""

import matplotlib.pyplot as plt
import numpy as np



def plot_energy_spectrum(pod_object, n_modes=None, figsize=(10, 5)):
    """
    Plot energy spectrum of POD modes, including individual and cumulative energy content.
    
    Parameters:
    -----------
    pod_object : object
        Object containing computed POD results with attributes 'energy_content' and 'cumulative_energy'.
    n_modes : int, optional
        Number of modes to plot. Defaults to min(15, total modes).
    figsize : tuple, optional
        Figure size. Default is (10, 5).
    """
    if not hasattr(pod_object, 'energy_content'):
        raise ValueError("POD not computed yet.")
    
    max_modes = n_modes or min(15, len(pod_object.energy_content))
    max_modes = min(max_modes, len(pod_object.energy_content))
    
    # Use a clean and modern plotting style
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize, sharex=True)
    
    # Style axes spines
    for ax in [ax1, ax2]:
        for spine in ax.spines.values():
            spine.set_edgecolor('black')
            spine.set_linewidth(2)
    
    bar_color = '#0072B2'      # Blue for bars
    line_color = '#009E73'     # Green for lines
    
    highlight_colors = {
        90: '#FCAE91',
        95: '#FB6A4A',
        99: '#CB181D'
    }
    
    # Individual energy content bar plot
    ax1.bar(range(1, max_modes + 1), pod_object.energy_content[:max_modes], color=bar_color)
    ax1.set_xlabel('POD Modes', fontsize=10)
    ax1.set_ylabel('Energy Content (%)', fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='y', direction='out', length=4, width=1, color='black')
    
    # Cumulative energy content line plot
    ax2.plot(range(1, max_modes + 1), pod_object.cumulative_energy[:max_modes], 'o-', 
             color=line_color, linewidth=2, markersize=4)
    for y_val, color in highlight_colors.items():
        ax2.axhline(y=y_val, color=color, linestyle='--', alpha=0.7, label=f'{y_val}%')
    ax2.set_xlabel('POD Modes', fontsize=10)
    ax2.set_ylabel('Cumulative Energy Content (%)', fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='y', direction='out', length=4, width=1, color='black')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig("pod_energy.tiff", dpi=600)
    plt.savefig("pod_energy.pdf", dpi=600)
    plt.show()
    
    # Print summary statistics
    print("\nEnergy Statistics:")
    print(f"First mode captures: {pod_object.energy_content[0]:.2f}% of energy")
    if len(pod_object.energy_content) >= 5:
        print(f"First 5 modes capture: {pod_object.cumulative_energy[4]:.2f}% of energy")
    
    for threshold in [90, 95, 99]:
        modes_needed = np.where(pod_object.cumulative_energy >= threshold)[0]
        if modes_needed.size > 0:
            print(f"Need {modes_needed[0] + 1} modes for {threshold}% energy")

    return fig

def plot_modes(pod_object, mode_indices, figsize=(12, 8)):
    """
    Plot spatial POD modes.
    
    Parameters:
    -----------
    pod_object : WeightedPOD
        Computed POD object
    mode_indices : list
        List of mode indices to plot
    figsize : tuple
        Figure size
    """
    if not hasattr(pod_object, 'phi_pod'):
        raise ValueError("POD not computed yet.")
    
    n_modes = len(mode_indices)
    fig, axes = plt.subplots(1, n_modes, figsize=figsize)
    if n_modes == 1:
        axes = [axes]
    
    for i, mode_idx in enumerate(mode_indices):
        im = axes[i].scatter(range(len(pod_object.phi_pod[:, mode_idx])), 
                           pod_object.phi_pod[:, mode_idx], 
                           c=pod_object.phi_pod[:, mode_idx], 
                           cmap='RdBu_r', s=1)
        axes[i].set_title(f'Mode {mode_idx+1} ({pod_object.energy_content[mode_idx]:.2f}%)')
        axes[i].set_xlabel('Spatial Point')
        axes[i].set_ylabel('Mode Amplitude')
        plt.colorbar(im, ax=axes[i])
    
    plt.tight_layout()
    return fig

def plot_reconstruction(original, reconstructed, snapshot_idx=0, figsize=(12, 5)):
    """
    Plot comparison between original and reconstructed fields.
    
    Parameters:
    -----------
    original : numpy.ndarray
        Original field
    reconstructed : numpy.ndarray
        Reconstructed field  
    snapshot_idx : int
        Snapshot index to plot
    figsize : tuple
        Figure size
    """
    fig, axes = plt.subplots(1, 3, figsize=figsize)
    
    # Original
    axes[0].plot(original[:, snapshot_idx])
    axes[0].set_title('Original')
    axes[0].set_xlabel('Spatial Point')
    axes[0].set_ylabel('Field Value')
    axes[0].grid(True, alpha=0.3)
    
    # Reconstructed
    axes[1].plot(reconstructed[:, snapshot_idx])
    axes[1].set_title('Reconstructed')
    axes[1].set_xlabel('Spatial Point')
    axes[1].set_ylabel('Field Value')
    axes[1].grid(True, alpha=0.3)
    
    # Error
    error = original[:, snapshot_idx] - reconstructed[:, snapshot_idx]
    axes[2].plot(error)
    axes[2].set_title('Error')
    axes[2].set_xlabel('Spatial Point')
    axes[2].set_ylabel('Error')
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig