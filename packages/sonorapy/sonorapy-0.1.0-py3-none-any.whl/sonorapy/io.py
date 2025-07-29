# -*- coding: utf-8 -*-
import os
import time

import numpy as np
import vtk
from vtk.util.numpy_support import numpy_to_vtk

from .h5 import get_h5_attribute, get_h5_dataset, get_h5_dataset_names


# %%
def get_sim_name(h5_file):
    return get_h5_attribute(h5_file, "/Metadata", "Name")


def get_dx(h5_file):
    return get_h5_attribute(h5_file, "/Domain", "dx")


def get_dt(h5_file):
    return get_h5_attribute(h5_file, "/Domain", "dt")


def get_c0(h5_file):
    return get_h5_attribute(h5_file, "/Materials/0/Properties", "c")


def get_snr0_position(h5_file):
    ijk = get_h5_dataset(h5_file, "/Sensors/Points/Grid/0", "ijk")
    xyz = get_h5_dataset(h5_file, "/Sensors/Points/Grid/0", "xyz")
    return {"ijk": ijk, "xyz": xyz}


def get_snapshot_dt(h5_file, sensor_key="Full"):
    # Retrieve dataset names and sort them
    field_sensors_root = f"/Sensors/Fields/{sensor_key}/"
    step = get_h5_attribute(h5_file, field_sensors_root, "Snapshot Step")
    dt = get_dt(h5_file)
    return step * dt


# %% Point Sensors
def get_point_sensors(h5_file, field_name="p(t)"):
    """
    Retrieve point sensor data from an HDF5 file.

    Parameters:
        h5_file (str): Path to the HDF5 file containing point sensor data.
        field_name (str): Name of the dataset to retrieve (default is "p(t)" for pressure).

    Returns:
        list of dict: A list where each element is a dictionary containing the ID, time series,
                      pressure series, and coordinates (x, y, z) of a point sensor.
    """
    point_sensors_root = r"/Output/Sensors/Points/Grid/"

    # Retrieve and sort the dataset names according to their integer values
    dset_nms = get_h5_dataset_names(h5_file, point_sensors_root)
    dset_nms.sort(key=int)
    dset_paths = [point_sensors_root + idx for idx in dset_nms]

    sensor_data = []
    for dset, dset_id in zip(dset_paths, dset_nms):
        x = get_h5_attribute(h5_file, dset, "x")
        y = get_h5_attribute(h5_file, dset, "y")
        z = get_h5_attribute(h5_file, dset, "z")
        t = get_h5_dataset(h5_file, dset, "t")
        out = get_h5_dataset(h5_file, dset, field_name)
        # Retrieve and apply the mask to filter the data if data is masked
        mask = get_h5_dataset(h5_file, dset, "Mask")
        if np.any(mask == 1):
            t = t[mask == 1]
            out = out[mask == 1]
        sensor_data.append(
            {"id": int(dset_id), "t": t, "p": out, "xyz": np.array([x, y, z])}
        )
    return sensor_data


# %% Sources
def get_sources(h5_file, field_name="p(t)"):
    """
    Retrieve source data from an HDF5 file.

    Parameters:
        h5_file (str): Path to the HDF5 file containing source data.
        field_name (str): Name of the dataset to retrieve (default is "p(t)" for pressure).

    Returns:
        list of dict: A list where each element is a dictionary containing the ID, time series,
                      pressure series, and coordinates (x, y, z) of a source.
    """
    sources_root = r"/Materials/"

    # Retrieve and sort the dataset names according to their integer values
    dset_nms = get_h5_dataset_names(h5_file, sources_root)
    dset_nms.sort(key=int)
    dset_paths = [sources_root + idx for idx in dset_nms]

    source_data = []
    for dset, dset_id in zip(dset_paths, dset_nms):
        x = get_h5_attribute(h5_file, dset, "x")
        y = get_h5_attribute(h5_file, dset, "y")
        z = get_h5_attribute(h5_file, dset, "z")
        t = get_h5_dataset(h5_file, dset, "t")
        out = get_h5_dataset(h5_file, dset, field_name)
        # Retrieve and apply the mask to filter the data if data is masked
        mask = get_h5_dataset(h5_file, dset, "Mask")
        if np.any(mask == 1):
            t = t[mask == 1]
            out = out[mask == 1]
        source_data.append(
            {"id": int(dset_id), "t": t, "p": out, "xyz": np.array([x, y, z])}
        )
    return source_data


# %% Field Sensors
def exp_field2vtk(
    h5_file,
    vtk_root,
    sensor_key="Full",
    field_name="p(x,y,z)",
    skip=0,
    log_trans=False,
    moving=False,
    to_clip=False,
    arctan_trans=False,
    Nmax=None,
):
    """
    Export field sensor data from an HDF5 file to VTK format for visualization.

    Parameters:
        h5_file (str): Path to the HDF5 file containing field sensor data.
        vtk_directory (str): Directory to save the VTK files.
        sensor_key (str): The key in the HDF5 file that contains the field sensor data.
        field_name (str): Name of the field to be exported.
        skip_interval (int): Interval at which to skip exporting frames (0 for no skipping).
        logarithmic_transform (bool): Apply logarithmic transformation to field data.
        moving_frame (bool): Adjust data for a moving frame of reference.
        copy_path_to_clipboard (bool): Copy the file pattern to clipboard after export.
        arctan_transform (bool): Apply arctan transformation to field data for 'compression'.

    Returns:
        None
    """
    sim_name = get_sim_name(h5_file)
    export_root = os.path.join(vtk_root, f"{sim_name}_{sensor_key}_")
    if "Subset" in sensor_key:
        import re

        sensor_value = "".join(re.findall(r"\d+", sensor_key))
        export_root = os.path.join(vtk_root, f"{sim_name}_Sub_{sensor_value}_")
    print(f"Exporting: {h5_file}")
    print(f"{sim_name}, key: {sensor_key}")

    # Retrieve dataset names and sort them
    field_sensors_root = f"/Output/Sensors/Fields/{sensor_key}/"
    dset_nms = get_h5_dataset_names(h5_file, field_sensors_root)
    dset_nms.sort(key=int)
    dset_paths = [field_sensors_root + idx for idx in dset_nms]

    # Get axes
    x = get_h5_dataset(h5_file, field_sensors_root, "X")
    y = get_h5_dataset(h5_file, field_sensors_root, "Y")
    z = get_h5_dataset(h5_file, field_sensors_root, "Z")

    print(f"Writing {len(dset_paths)} fields")
    start_time = time.time()

    # Process and export each dataset
    # Iterate over fields, start at 0, skip over if necessary
    for i, (dset, dset_id) in enumerate(zip(dset_paths, dset_nms)):
        if i % (skip + 1) == 0:
            field_data = get_h5_dataset(h5_file, dset, field_name)
            # Pre processing before writing
            # Used to pretend we have a logarithmic color scale
            if log_trans:
                # Log scale transformation for positive and negative values
                field_pos = np.maximum(field_data, 0)
                field_neg = np.abs(np.minimum(field_data, 0))
                # log10 transformation +1
                log_pos = np.ma.log10(
                    1 + np.ma.masked_where(field_pos <= 0, field_pos)
                ).filled(0)
                log_neg = np.ma.log10(
                    1 + np.ma.masked_where(field_neg <= 0, field_neg)
                ).filled(0)
                field_data = log_pos - log_neg
            # Arctan 'compressed' color scale
            elif arctan_trans:
                field_data = np.arctan(field_data)

            x_offset = get_h5_attribute(h5_file, dset, "x_offset") if moving else 0
            write_vtk_3d(
                field_data, x + x_offset, y, z, export_root, field_name, dset_id
            )

        if i % 10 == 0:
            elapsed = time.time() - start_time
            it_left = np.size(dset_paths) - i - 1
            v_est = (i + 1) / elapsed
            t_est = it_left / v_est
            print(f"{i}/{np.size(dset_paths)-1} : Est. time left {t_est:.2f} s")

        if Nmax is not None and i > Nmax:
            break

    print("Finished exporting field sensors to Vtk")

    # Write out file pattern
    export_file_pattern = export_root.replace("\\", "/") + "..vtr"
    print(export_file_pattern)


def exp_vox2vtk(h5_file, vtk_root):
    """
    Export field sensor data from an HDF5 file to VTK format for visualization.

    Parameters:
        h5_file (str): Path to the HDF5 file containing voxel data.
        vtk_directory (str): Directory to save the VTK files.

    Returns:
        None
    """
    sim_name = get_sim_name(h5_file)
    export_root = os.path.join(vtk_root, f"{sim_name}_voxels")
    print(f"Exporting: {h5_file} to {export_root}")

    # Get axes
    voxels = get_h5_dataset(h5_file, "/Domain/", "Material Voxels")
    x = get_h5_dataset(h5_file, "/Domain/", "X")
    y = get_h5_dataset(h5_file, "/Domain/", "Y")
    z = get_h5_dataset(h5_file, "/Domain/", "Z")

    write_vtk_3d_surfaces(voxels, x, y, z, export_root, "Materials")

    print("Finished exporting voxels to Vtk")
    print(f"{export_root}.vtm")


def exp_pts2vtk(h5_file, vtk_root, indices=None, suffix=""):
    """
    Export point sensor data (sources and receivers) from an HDF5 file to VTK format for visualization.

    Parameters:
        h5_file (str): Path to the HDF5 file containing point sensor data.
        vtk_directory (str): Directory to save the VTK files.
        indices (list, optional): List of indices to export a subset of point sensors. If None, export all.
        suffix (str, optional): Suffix to add to the export root directory name.

    Returns:
        None
    """
    sim_name = get_sim_name(h5_file)
    if suffix:
        suffix = f"_{suffix}"
    export_root = os.path.join(vtk_root, f"{sim_name}_points{suffix}")
    print(f"Exporting: {h5_file} to {export_root}")

    # Get point sensors
    pt_snrs = get_point_sensors(h5_file)
    points = []
    if indices is None:
        indices = range(len(pt_snrs))
    for idx in indices:
        pt = pt_snrs[idx]
        points.append(pt["xyz"])
        print(f" Point sensor: {idx}")
    write_vtk_points(points, export_root)

    print("Finished exporting points to Vtk")
    print(f"{export_root}.vtk")


# %% Vtk write
def write_vtk_3d(
    out,
    x_axis,
    y_axis,
    z_axis,
    output_path,
    field_name,
    output_name="",
    data_type="point",
):
    """
    Write data to a VTK Rectilinear Grid file.

    Parameters:
        out (np.ndarray): The data to write.
        x, y, z (array-like): Coordinates of the grid points.
        output_path (str): The directory to write the output VTK file.
        field_name (str): The name of the field in the VTK file.
        data_type (str): The type of data being written ('point' or 'voxel').
        output_name (str, optional): The name of the output VTK file. Defaults to an empty string.

    Returns:
        None
    """
    # Create vtkImageData for uniform grid
    # Using vtkImageData instead of rectilinear grid for uniform grid
    grid = vtk.vtkImageData()
    if data_type == "voxel":
        grid.SetDimensions(len(x_axis) + 1, len(y_axis) + 1, len(z_axis) + 1)
    else:
        grid.SetDimensions(len(x_axis), len(y_axis), len(z_axis))

    # Set the origin and spacing
    if len(x_axis) > 1:
        dx = x_axis[1] - x_axis[0]
    elif len(y_axis) > 1:
        dx = y_axis[1] - y_axis[0]
    elif len(z_axis) > 1:
        dx = z_axis[1] - z_axis[0]
    else:
        dx = 1

    if data_type == "voxel":
        grid.SetOrigin(x_axis[0] - dx / 2, y_axis[0] - dx / 2, z_axis[0] - dx / 2)
    else:
        grid.SetOrigin(x_axis[0], y_axis[0], z_axis[0])
    grid.SetSpacing((dx, dx, dx))

    # Prepare the data array
    vtk_data = numpy_to_vtk(out.flatten(), deep=True)
    vtk_data.SetName(field_name)

    # Add the data to the grid
    if data_type == "voxel":
        grid.GetCellData().SetScalars(vtk_data)
    else:
        grid.GetPointData().SetScalars(vtk_data)

    # Determine the file name and write the data to a file
    file_name = f"{output_path}{output_name}.vti"
    writer = vtk.vtkXMLImageDataWriter()
    writer.SetFileName(file_name)
    writer.SetInputData(grid)
    writer.Write()


def write_vtk_3d_surfaces(
    out, x_axis, y_axis, z_axis, output_path, field_name, output_name=""
):
    """
    Write voxel data to VTK multiblock file as a collection of surfaces (from cell data, not point data).
    Each surface corresponds to the different materials. This helps to visualize the materials efficiently in 3D space.

    Parameters:
        out (np.ndarray): The data to write.
        x_axis, y_axis, z_axis (array-like): Coordinates of the grid points.
        output_path (str): The directory to write the output VTK file.
        field_name (str): The name of the field in the VTK file.
        output_name (str, optional): The name of the output VTK file. Defaults to an empty string.

    Returns:
        None
    """
    # Create vtkImageData for uniform grid (using cell data instead of point data)
    image_data = vtk.vtkImageData()
    image_data.SetDimensions(
        len(x_axis) + 1, len(y_axis) + 1, len(z_axis) + 1
    )  # +1 to shift to cell data

    # Set the origin and spacing for cells
    if len(x_axis) > 1:
        dx = x_axis[1] - x_axis[0]
    elif len(y_axis) > 1:
        dx = y_axis[1] - y_axis[0]
    elif len(z_axis) > 1:
        dx = z_axis[1] - z_axis[0]
    else:
        dx = 1
    image_data.SetOrigin(x_axis[0], y_axis[0], z_axis[0])
    image_data.SetSpacing(dx, dx, dx)

    # Set cell data (convert numpy to vtk type)
    vtk_data = numpy_to_vtk(out.flatten(), deep=True, array_type=vtk.VTK_INT)
    vtk_data.SetName(field_name)
    image_data.GetCellData().SetScalars(vtk_data)

    # Create a vtkMultiBlockDataSet to store all surfaces
    multi_block_data = vtk.vtkMultiBlockDataSet()
    block_index = 0

    # Extract surfaces for each material
    for material_id in np.unique(out):
        # Skip empty space
        if material_id == 0:
            continue

        # Threshold the data to extract the material
        threshold = vtk.vtkThreshold()
        threshold.SetInputData(image_data)
        threshold.SetLowerThreshold(material_id)
        threshold.SetUpperThreshold(material_id)
        threshold.SetThresholdFunction(vtk.vtkThreshold.THRESHOLD_BETWEEN)
        threshold.Update()

        # Extract the surface of the thresholded data
        surface_filter = vtk.vtkDataSetSurfaceFilter()
        surface_filter.SetInputData(threshold.GetOutput())
        surface_filter.Update()

        # Add the surface to the multi-block dataset
        multi_block_data.SetBlock(block_index, surface_filter.GetOutput())
        block_index += 1

    # Write the multi-block dataset to a vtk file
    writer = vtk.vtkXMLMultiBlockDataWriter()
    writer.SetFileName(f"{output_path}{output_name}.vtm")
    writer.SetInputData(multi_block_data)
    writer.Write()


def write_vtk_surf(z_surface, x_axis, y_axis, file_path="", file_name="Surface"):
    """
    Writes a structured grid VTK file representing a surface defined by the z_surface array.

    Parameters:
        z_surface (numpy.ndarray): A 2D array representing the surface elevation data.
        x_axis (numpy.ndarray): Array of x-coordinates.
        y_axis (numpy.ndarray): Array of y-coordinates.
        file_path (str, optional): Directory path where the VTK file will be saved. Defaults to the current directory.
        file_name (str, optional): Name of the VTK file without the extension. Defaults to "Surface".

    Returns:
        None: The function writes a file to the disk and does not return any value.
    """
    # Create a meshgrid from the x and y axes for the structured grid
    x_grid, y_grid = np.meshgrid(x_axis, y_axis, indexing="ij")
    num_points_x, num_points_y = z_surface.shape

    # Initialize a vtkPoints object to store the grid points
    points = vtk.vtkPoints()
    points.SetNumberOfPoints(num_points_x * num_points_y)

    # Populate the vtkPoints object with coordinates from the surface data
    for i in range(num_points_x):
        for j in range(num_points_y):
            idx = i * num_points_y + j
            points.SetPoint(idx, x_grid[i, j], y_grid[i, j], z_surface[i, j])

    # Set up the structured grid with the points
    structured_grid = vtk.vtkStructuredGrid()
    structured_grid.SetDimensions(
        num_points_y, num_points_x, 1
    )  # Note the order of dimensions
    structured_grid.SetPoints(points)

    # Configure the VTK writer and output the structured grid to a file
    writer = vtk.vtkStructuredGridWriter()
    full_file_path = f"{file_path}/{file_name}.vtk"
    writer.SetFileName(full_file_path)
    writer.SetInputData(structured_grid)
    writer.Write()

    print(f"Surface data exported to: {full_file_path}")


def write_vtk_points(points, output_path):
    # Create a vtkPoints object and add the points to it
    vtk_points = vtk.vtkPoints()
    for point in points:
        vtk_points.InsertNextPoint(point)

    # Create a vtkPolyData object and set the points to it
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(vtk_points)

    # Create a vertex for each point. vtkPolyVertex requires all points at once.
    vertices = vtk.vtkCellArray()
    for i in range(vtk_points.GetNumberOfPoints()):
        vertex = vtk.vtkVertex()
        vertex.GetPointIds().SetId(0, i)  # Set the id of the vertex point
        vertices.InsertNextCell(vertex)

    polydata.SetVerts(vertices)

    # Write to a VTK file
    writer = vtk.vtkPolyDataWriter()
    writer.SetFileName(f"{output_path}.vtk")
    writer.SetInputData(polydata)
    writer.Write()


def create_video_from_images(
    inout_path, input_pattern, output_name, framerate=10, crf=18, pix_fmt="yuv420p"
):
    """
    Create a video from a sequence of images using ffmpeg. Note: this overwrites existing output files.
    Output command copied to clipboard.

    Args:
        inout_path (str): Path where input images are located and output will be saved
        input_pattern (str): Pattern for input images (e.g., 'frame_%d.png')
        output_name (str): Name of the mp4 output video file (e.g., 'output')
        framerate (int): Frames per second for the output video
        crf (int): Constant Rate Factor for quality (0-51, lower is better quality)
        pix_fmt (str): Pixel format for the output video
    """
    import os
    import subprocess

    # Construct full paths
    input_path = os.path.join(inout_path, input_pattern)
    output_path = os.path.join(inout_path, output_name + ".mp4")

    # Command string for reference
    command_string = (
        f"ffmpeg -y -framerate {framerate} "
        f'-i "{input_path}" '
        f"-c:v libx264 "
        f"-crf {crf} "
        f"-pix_fmt {pix_fmt} "
        f'"{output_path}"'
    )
    import pandas.io.clipboard as pyperclip

    pyperclip.copy(command_string)

    print(command_string)

    try:
        # Run with stdout and stderr passed through to see real-time output
        process = subprocess.Popen(
            command_string,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
        )

        # Print output in real-time
        for line in process.stdout:
            print(line, end="")

        # Wait for process to complete and get return code
        return_code = process.wait()

        if return_code == 0:
            print(f"\nSuccessfully created video at: {output_path}")
        else:
            print(f"\nError: ffmpeg exited with code {return_code}")

    except FileNotFoundError:
        print(
            "Error: ffmpeg not found. Please ensure ffmpeg is installed and in your system PATH."
        )
    except Exception as e:
        print(f"Error creating video: {e}")
