import os
import re
import numpy as np
import gc
import pandas as pd
import fluidfoam.readof  
import fluidfoam

def read_files(base_folder):
    """
    Parameters
    ----------
    base_folder : str
        Main directory path.
        Find only folders starting with 'Re' and
        assign the path of these folders into dict.

    Returns
    -------
    dict
        {folder_name : full_path}
    """
    contents = {}
    for folder in os.listdir(base_folder):
        folder_path = os.path.join(base_folder, folder)
        if os.path.isdir(folder_path) and folder.startswith("Re"):
            contents[folder] = folder_path
    return contents


def parse_case_name(name):
    """
    Parameters
    ----------
    name : str
        Folder name

    Returns
    -------
    tuple
        (Reynolds number (float), angle (int))
    """
    re_match = re.search(r'Re([\d.]+)', name)
    a_match = re.search(r'a(\d+)', name)  # a'n?n yan?na + koydum, tek haneli olmak zorunda de?il

    re_val = float(re_match.group(1)) if re_match else None
    a_val = int(a_match.group(1)) if a_match else None

    return re_val, a_val


def load_fluidfoam_data(postprocess_path="postProcess"):
    """
    Parameters
    ----------
    postprocess_path : str
        Path to the postProcess directory containing cases.

    Returns
    -------
    Ux_dict : dict
    Uy_dict : dict
    Uz_dict : dict
    Re_list : list
        Sorted list of unique Reynolds numbers.
    """
    print("1. Loading FluidFoam data...")
    data = []
    paths = read_files(postprocess_path)
    for case_name, case_path in paths.items():
        U = fluidfoam.readof.readvector(case_path, time_name='0', name='pa(U)')
        Re_val, a_val = parse_case_name(case_name)
        data.append({"case": case_name, "Re": Re_val, "a": a_val, "velocity": U})

    df = pd.DataFrame(data).sort_values(["Re", "a"]).reset_index(drop=True)

    # Get prefixes for unique cases (e.g. Re100_a5)
    prefixes = df['case'].str.extract(r'^(Re[^_]+_a\d+)')[0].unique()

    print("Loading velocity data...")
    velocities = {}
    for i, p in enumerate(prefixes, 1):
        vel = df[df['case'].str.startswith(p + '_')]['velocity'].iloc[0]
        velocities[p] = vel.T
        if i % 20 == 0:
            print(f"  Loaded {i} velocity fields...")

    angles = list(range(5, 95, 5))
    Re_list = sorted({p.split('_')[0] for p in prefixes})
    print(f"Available Reynolds numbers: {Re_list}")
    print(f"Available angles: {angles}")

    print("Organizing velocity components...")
    Ux_dict, Uy_dict, Uz_dict = {}, {}, {}

    for Re in Re_list:
        ux, uy, uz = [], [], []
        valid_angles = []

        for a in angles:
            key = f"{Re}_a{a}"
            if key in velocities:
                U = velocities[key]
                ux.append(U[:, 0])
                uy.append(U[:, 1])
                uz.append(U[:, 2])
                valid_angles.append(a)

        if ux:
            Ux_dict[Re] = np.array(ux, dtype=np.float32).T
            Uy_dict[Re] = np.array(uy, dtype=np.float32).T
            Uz_dict[Re] = np.array(uz, dtype=np.float32).T
            print(f"Data loaded for {Re}: {len(valid_angles)} angles, shape: {Ux_dict[Re].shape}")

    del velocities
    gc.collect()

    return Ux_dict, Uy_dict, Uz_dict, Re_list


def load_data_Volume(volume_path):
    global_volumes = fluidfoam.readof.readscalar(volume_path, time_name='0' , name='Vc')
    global_volumes = global_volumes.astype(np.float32)
    print(f"? Loaded actual cell volumes from OpenFOAM: {global_volumes.shape}")
    return global_volumes