# -*- coding: utf-8 -*-
# %%
def solve(
    input_file,
    prog_path=r"D:\dev\sonora\build\RelWithDebInfo\sonora.exe",
    verbose=True,
):
    # Run executable
    import subprocess

    p = subprocess.Popen([prog_path, input_file], stdout=subprocess.PIPE)
    # Read and print the output line by line as it becomes available
    while True:
        output = p.stdout.readline()
        if output == b"" and p.poll() is not None:
            break
        if output and verbose:
            print(output.strip().decode())
    if p.returncode != 0:
        print("Exited with errors, code: ", p.returncode)


# %% FDTD
def fmax2dx(f_max, ppw=10, c0=343.575):
    wavelength = c0 / f_max
    dx = wavelength / 10
    return dx


def dx2fmax(dx, ppw=10, c0=343.575):
    wavelength = dx * 10
    f_max = c0 / wavelength
    return f_max


# %%
class SimulationParameters:
    def __init__(self):
        import empapuLib_InputFile as eLif

        # Solver settings
        self.solver = eLif.Solver.PV3dGpu

        # Spatial domain
        self.dx = None  # Placeholder; assign a value when initializing
        self.Lx = None
        self.Ly = None
        self.Lz = None

        # Background
        self.rho0 = 1.2
        self.c0 = 343.575

        # Temporal domain
        self.T = None
        self.courant = 0.9

        # Material type assignment
        self.ids_hard = []
        self.ids_lr_0 = []
        self.ids_src_p = []
        self.ids_src_v = []

        # Materials to remove
        self.ids_del = []

        # Media
        self.mediums = [{"id": 0, "rho": self.rho0, "c": self.c0}]

        # Reflectors
        self.bc_reflectors = [{"ids": self.ids_hard}]

        # IIR1s
        self.bc_iir1s = [
            {
                "ids": self.ids_lr_0,
                "k_a1": 0.0,
                "k_b0": 1.0,
                "k_b1": 0.0,
                "c": self.c0,
                "geometry": eLif.Indices.fromVoxels,
            }
        ]

        # Sources
        self.srcs_p = [
            {
                "ids": self.ids_src_p,
                "signal": None,
                "xyz": None,
                "geometry": eLif.Indices.setManually,
            }
        ]
        self.srcs_v = [
            {
                "ids": self.ids_src_v,
                "signal": None,
                "xyz": None,
                "geometry": eLif.Indices.setManually,
            }
        ]

        # Boundaries
        self.boundary_xn = eLif.BoundaryLayer.Neumann
        self.boundary_xp = eLif.BoundaryLayer.Neumann
        self.boundary_yn = eLif.BoundaryLayer.Neumann
        self.boundary_yp = eLif.BoundaryLayer.Neumann
        self.boundary_zn = eLif.BoundaryLayer.Neumann
        self.boundary_zp = eLif.BoundaryLayer.Neumann

        # PML
        self.pml_r0 = 1e-20
        self.pml_m = 4
        self.pml_x0 = 0
        self.pml_xl = 0
        self.pml_y0 = 0
        self.pml_yl = 0
        self.pml_z0 = 0
        self.pml_zl = 0

        # Point sensors
        self.mics_xyz = []

        # Field sensors - 3D, 2D, and subdomains
        self.field_3d = [{"n": 1, "n_max": 0, "n_step": None}]
        self.field_3d_full = False
        self.field_3d_inner = False

        self.field_2d = [{"n": 1, "n_max": 0, "n_step": None}]
        self.field_2d_src_xy = False
        self.field_2d_src_xz = False
        self.field_2d_src_yz = False

        self.field_subdomains = [
            {"n": None, "n_max": 0, "n_step": None, "xyz_min": None, "xyz_max": None}
        ]

        # Voxel operations
        self.vox_ops = []


def diff_parameters(param_ref, param_eval):
    import numpy as np

    differences = {}
    for key in param_ref.__dict__:
        ref_value = param_ref.__dict__[key]
        eval_value = param_eval.__dict__.get(key, None)

        if isinstance(ref_value, np.ndarray) and isinstance(eval_value, np.ndarray):
            if not np.array_equal(ref_value, eval_value):
                differences[key] = (ref_value, eval_value)
        elif ref_value != eval_value:
            differences[key] = (ref_value, eval_value)
    return differences
