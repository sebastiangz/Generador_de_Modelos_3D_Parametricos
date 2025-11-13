"""
src.csg
Implementación de Constructive Solid Geometry (CSG) funcional.
"""

from dataclasses import dataclass
from typing import Callable, Tuple, List
from .vectors import Vector3, Matrix4x4

# Un Bounding Box (caja delimitadora) se define por dos vectores
Bounds = Tuple[Vector3, Vector3]

# --- Funciones auxiliares para Bounding Boxes ---

def comb
    """Crea un Bounding Box que envuelve otros dos"""
    min_v = Vector3(
        min(b1[0].x, b2[0].x),ine_bounds(b1: Bounds, b2: Bounds) -> Bounds:
        min(b1[0].y, b2[0].y),
        min(b1[0].z, b2[0].z)
    )
    max_v = Vector3(
        max(b1[1].x, b2[1].x),
        max(b1[1].y, b2[1].y),
        max(b1[1].z, b2[1].z)
    )
    return (min_v, max_v)

def intersect_bounds(b1: Bounds, b2: Bounds) -> Bounds:
    """Crea un Bounding Box de la intersección de otros dos"""
    min_v = Vector3(
        max(b1[0].x, b2[0].x),
        max(b1[0].y, b2[0].y),
        max(b1[0].z, b2[0].z)
    )
    max_v = Vector3(
        min(b1[1].x, b2[1].x),
        min(b1[1].y, b2[1].y),
        min(b1[1].z, b2[1].z)
    )
    # Si no hay intersección, min > max
    if min_v.x > max_v.x or min_v.y > max_v.y or min_v.z > max_v.z:
        return (Vector3(0,0,0), Vector3(0,0,0))
    return (min_v, max_v)

def transform_bounds(bounds: Bounds, matrix: Matrix4x4) -> Bounds:
    """Transforma un Bounding Box y calcula el nuevo AABB que lo envuelve"""
    b_min, b_max = bounds
    # Los 8 vértices del Bounding Box
    corners = [
        Vector3(b_min.x, b_min.y, b_min.z),
        Vector3(b_max.x, b_min.y, b_min.z),
        Vector3(b_min.x, b_max.y, b_min.z),
        Vector3(b_min.x, b_min.y, b_max.z),
        Vector3(b_max.x, b_max.y, b_min.z),
        Vector3(b_min.x, b_max.y, b_max.z),
        Vector3(b_max.x, b_min.y, b_max.z),
        Vector3(b_max.x, b_max.y, b_max.z),
    ]
    
    transformed_corners = [matrix.apply_to_vector(c) for c in corners]
    
    new_min = Vector3(
        min(c.x for c in transformed_corners),
        min(c.y for c in transformed_corners),
        min(c.z for c in transformed_corners)
    )
    new_max = Vector3(
        max(c.x for c in transformed_corners),
        max(c.y for c in transformed_corners),
        max(c.z for c in transformed_corners)
    )
    return (new_min, new_max)