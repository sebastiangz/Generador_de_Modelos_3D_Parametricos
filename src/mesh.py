"""
src.mesh
Funciones para "meshing" (mallado) de representaciones funcionales.
"""

import numpy as np
import trimesh
from skimage.measure import marching_cubes 
from typing import Tuple, Optional

from .csg import Solid
from .vectors import Vector3
from .surfaces import ParametricSurface

def mesh_from_solid(solid: Solid, resolution: int = 50) -> trimesh.Trimesh:
    resolution = max(2, resolution)
    b_min, b_max = solid.bounds

    if b_min == b_max or np.any(np.isinf([b_min.x, b_min.y, b_min.z, b_max.x, b_max.y, b_max.z])):
        return trimesh.Trimesh()

    x_range = b_max.x - b_min.x
    y_range = b_max.y - b_min.y
    z_range = b_max.z - b_min.z

    x = np.linspace(b_min.x, b_max.x, resolution)
    y = np.linspace(b_min.y, b_max.y, resolution)
    z = np.linspace(b_min.z, b_max.z, resolution)

    xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
    grid_points = np.stack([xx.ravel(), yy.ravel(), zz.ravel()], axis=-1)

    try:
        vector3_points = (Vector3(p[0], p[1], p[2]) for p in grid_points)
        scalar_field = np.array(
            [solid.contains(v) for v in vector3_points],
            dtype=float
        ).reshape(resolution, resolution, resolution)
    except Exception:
        return trimesh.Trimesh()

    if not np.any(scalar_field > 0):
        return trimesh.Trimesh()

    spacing = (
        x_range / (resolution - 1),
        y_range / (resolution - 1),
        z_range / (resolution - 1)
    )

    try:
        vertices, faces, _, _ = marching_cubes(
            scalar_field,
            level=0.5, 
            spacing=spacing
        )
    except Exception:
        return trimesh.Trimesh()

    if vertices.size == 0:
        return trimesh.Trimesh()

    vertices += [b_min.x, b_min.y, b_min.z]

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    mesh.fix_normals()
    
    return mesh

def mesh_from_surface(
    surface_fn: ParametricSurface,
    u_range: Tuple[float, float] = (0, 1),
    v_range: Tuple[float, float] = (0, 1),
    u_steps: int = 30,
    v_steps: int = 30
) -> trimesh.Trimesh:
    u_vals = np.linspace(u_range[0], u_range[1], u_steps)
    v_vals = np.linspace(v_range[0], v_range[1], v_steps)

    vertices = []
    for u in u_vals:
        for v in v_vals:
            vec = surface_fn(u, v)
            vertices.append([vec.x, vec.y, vec.z])

    vertices_np = np.array(vertices)
    faces = []
    
    for i in range(u_steps - 1):
        for j in range(v_steps - 1):
            p1 = i * v_steps + j
            p2 = i * v_steps + (j + 1)
            p3 = (i + 1) * v_steps + (j + 1)
            p4 = (i + 1) * v_steps + j

            faces.append([p1, p3, p2])
            faces.append([p1, p4, p3])

    mesh = trimesh.Trimesh(vertices=vertices_np, faces=np.array(faces))
    mesh.fix_normals()

    return mesh