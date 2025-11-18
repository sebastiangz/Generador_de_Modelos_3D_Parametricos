"""
src.mesh
Funciones para "meshing" (mallado) de representaciones funcionales.

Convierte un `Solid` (CSG) o una `ParametricSurface` en un
objeto `trimesh.Trimesh` (vértices y caras), que es lo que
se necesita para exportar a STL u OBJ.
"""

import numpy as np
import trimesh
# Marching cubes es el algoritmo para convertir
# campos escalares implícitos (como `solid.contains`) en mallas.
from trimesh.voxel.creation import marching_cubes
from typing import Callable
from .csg import Solid
from .vectors import Vector3
from .surfaces import ParametricSurface

def mesh_from_solid(solid: Solid, resolution: int = 50) -> trimesh.Trimesh:
    """
    Genera un mesh (malla) a partir de un Sólido CSG usando
    el algoritmo Marching Cubes.

    Args:
        solid: El objeto Solid funcional.
        resolution: El número de cubos por eje para muestrear.
                    Valores más altos = más detalle, más lento.
    """
    b_min, b_max = solid.bounds

    # Asegurarse de que los límites no sean un punto/línea
    if b_min == b_max or np.any(np.isinf([b_min.x, b_min.y, b_min.z, b_max.x, b_max.y, b_max.z])):
        print("Advertencia: Límites del sólido inválidos o colapsados.")
        return trimesh.Trimesh() # Mesh vacío

    # 1. Crear la rejilla de puntos para muestrear
    x = np.linspace(b_min.x, b_max.x, resolution)
    y = np.linspace(b_min.y, b_max.y, resolution)
    z = np.linspace(b_min.z, b_max.z, resolution)

    xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')

    # Puntos en formato (N, 3)
    grid_points = np.stack([xx.ravel(), yy.ravel(), zz.ravel()], axis=-1)

    # 2. Muestrear la función 'contains' del sólido en la rejilla
    # Esto es O(N^3) y llama a una función de Python, es la parte lenta.
    try:
        # Convertimos los puntos numpy a objetos Vector3 para `solid.contains`
        vector3_points = (Vector3(p[0], p[1], p[2]) for p in grid_points)
        scalar_field = np.array(
            [solid.contains(v) for v in vector3_points],
            dtype=float # Usamos float (0.0 o 1.0)
        ).reshape(resolution, resolution, resolution)

    except Exception as e:
        print(f"Error durante el muestreo del Sólido: {e}")
        return trimesh.Trimesh()

    if not np.any(scalar_field > 0):
        # El campo escalar está vacío (todo 0.0), no hay geometría
        print("Advertencia: El muestreo del sólido no generó geometría (campo vacío).")
        return trimesh.Trimesh()

    # 3. Calcular Marching Cubes
    # `pitch` es el tamaño (ancho, alto, profundo) de cada celda voxel
    pitch = (
        (b_max.x - b_min.x) / (resolution - 1),
        (b_max.y - b_min.y) / (resolution - 1),
        (b_max.z - b_min.z) / (resolution - 1)
    )

    try:
        # Marching cubes encuentra la superficie en el nivel 0.5
        vertices, faces, _normals, _values = marching_cubes(
            scalar_field,
            level=0.5, # La superficie está entre 0.0 (fuera) y 1.0 (dentro)
            pitch=pitch
        )
    except Exception as e:
        # A veces falla si no hay superficie (ej. todo dentro o todo fuera)
        print(f"Error en Marching Cubes (trimesh): {e}")
        return trimesh.Trimesh()

    if vertices.size == 0:
        return trimesh.Trimesh()

    # 4. Ajustar la posición de los vértices
    # Marching cubes genera vértices desde (0,0,0).
    # Necesitamos trasladarlos al Bounding Box original (sumar el min).
    vertices += [b_min.x, b_min.y, b_min.z]

    return trimesh.Trimesh(vertices=vertices, faces=faces)

def mesh_from_surface(
    surface_fn: ParametricSurface,
    u_range: tuple = (0, 1),
    v_range: tuple = (0, 1),
    u_steps: int = 30,
    v_steps: int = 30
) -> trimesh.Trimesh:
    """
    Genera un mesh (malla) a partir de una superficie paramétrica
    muestreando una rejilla UV.
    """
    u_vals = np.linspace(u_range[0], u_range[1], u_steps)
    v_vals = np.linspace(v_range[0], v_range[1], v_steps)

    vertices = []
    # Generar todos los vértices
    for u in u_vals:
        for v in v_vals:
            vec = surface_fn(u, v)
            vertices.append([vec.x, vec.y, vec.z])

    vertices_np = np.array(vertices)

    faces = []
    # Generar caras (quads divididos en 2 triángulos)
    for i in range(u_steps - 1):
        for j in range(v_steps - 1):
            # Índices de los 4 vértices del quad en la rejilla
            # (i, j) -> p1
            # (i, j+1) -> p2
            # (i+1, j+1) -> p3
            # (i+1, j) -> p4
            p1 = i * v_steps + j
            p2 = i * v_steps + (j + 1)
            p3 = (i + 1) * v_steps + (j + 1)
            p4 = (i + 1) * v_steps + j

            # Triángulo 1 (p1, p2, p3)
            faces.append([p1, p2, p3])
            # Triángulo 2 (p1, p3, p4)
            faces.append([p1, p3, p4])

    return trimesh.Trimesh(vertices=vertices_np, faces=np.array(faces))