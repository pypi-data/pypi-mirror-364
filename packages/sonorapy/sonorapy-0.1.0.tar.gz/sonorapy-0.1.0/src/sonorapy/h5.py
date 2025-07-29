# -*- coding: utf-8 -*-
import h5py
import numpy as np


def get_h5_attribute(h5f, group_name, attribute_name):
    """
    Retrieve an attribute from a specific group in an HDF5 file.

    Parameters:
        h5f (str): The file path of the HDF5 file.
        group_name (str): The name of the group where the attribute resides.
        attribute_name (str): The name of the attribute to retrieve.

    Returns:
        The value of the specified attribute.
    """
    with h5py.File(h5f, "r") as f:
        return f[group_name].attrs[attribute_name]


def get_h5_dataset(h5f, group_name, dataset_name):
    """
    Retrieve a dataset from a specific group in an HDF5 file.

    Parameters:
        h5f (str): The file path of the HDF5 file.
        group_name (str): The name of the group where the dataset resides.
        dataset_name (str): The name of the dataset to retrieve.

    Returns:
        np.ndarray: The dataset as a NumPy array.
    """
    with h5py.File(h5f, "r") as f:
        dataset_path = f"{group_name}/{dataset_name}"
        if dataset_path not in f:
            print(f"Could not find dataset {dataset_name} in {group_name}")
            return None
        return f[dataset_path][()]


def find_h5_dataset(h5f, group_name, dataset_name):
    """
    Find a dataset in an HDF5 file where the dataset name contains a given substring.

    Parameters:
        h5f (str): The file path of the HDF5 file.
        group_name (str): The name of the group to initiate search.
        dataset_name (str): The substring to search for in dataset names.

    Returns:
        np.ndarray: The found dataset as a NumPy array.
    """
    with h5py.File(h5f, "r") as f:

        def find_dataset(name):
            if dataset_name in name:
                return name

        found_dataset = f[group_name].visit(find_dataset)
        return f[f"{group_name}/{found_dataset}"][()]


def find_h5_group(h5f, group_name, target_group):
    """
    Find a group in an HDF5 file where the group name contains a given substring.

    Parameters:
        h5f (str): The file path of the HDF5 file.
        group_name (str): The name of the parent group to initiate search.
        target_group (str): The substring to search for in group names.

    Returns:
        str: The full path of the found group.
    """
    with h5py.File(h5f, "r") as f:

        def find_group(name):
            if target_group in name and isinstance(f[group_name][name], h5py.Group):
                return name

        found_group = f[group_name].visit(find_group)
        return f"{group_name}/{found_group}" if found_group else None


def set_h5_dataset(h5f, group_name, dataset_name, data):
    """
    Set a dataset's value in a specific group in an HDF5 file.

    Parameters:
        h5f (str): The file path of the HDF5 file.
        group_name (str): The name of the group where the dataset resides.
        dataset_name (str): The name of the dataset to set.
        data (np.ndarray): The data to set.

    Returns:
        bool: True if operation is successful, False otherwise.
    """
    with h5py.File(h5f, "r+") as f:
        dataset_path = f"{group_name}/{dataset_name}"
        if dataset_path not in f:
            return False
        f[dataset_path][()] = data
        return True


def get_h5_dataset_names(h5f, group_name):
    """
    Retrieve all dataset names within a specific group in an HDF5 file.

    Parameters:
        h5f (str): The file path of the HDF5 file.
        group_name (str): The name of the group to look into.

    Returns:
        list: A list of dataset paths.
    """
    dataset_paths = []

    def visitor_func(name, node):
        if isinstance(node, h5py.Group):
            dataset_paths.append(name)

    with h5py.File(h5f, "r") as f:
        f[group_name].visititems(visitor_func)
    return dataset_paths


def print_h5_dataset_attributes(h5f, group_name, dataset_name):
    """
    Print all attributes of a specific dataset in an HDF5 file.

    Parameters:
        h5f (str): The file path of the HDF5 file.
        group_name (str): The name of the group where the dataset resides.
        dataset_name (str): The name of the dataset whose attributes to print.
    """
    with h5py.File(h5f, "r") as f:
        dataset_path = f"{group_name}/{dataset_name}"
        if dataset_path not in f:
            print(f"Could not find dataset {dataset_name} in {group_name}")
            return
        for key, value in f[dataset_path].attrs.items():
            print(f"{key} : {value}")
