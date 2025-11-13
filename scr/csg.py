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


@dataclass(frozen=True)
class Solid:
    """
    Representación funcional e inmutable de un sólido 3D.

    Atributos:
        contains (Callable): Una función (Vector3) -> bool.
                             Retorna True si el punto está dentro del sólido.
        bounds (Bounds): Una tupla (Vector3_min, Vector3_max)
                         que define la caja delimitadora del sólido.
    """
    contains: Callable[[Vector3], bool]
    bounds: Bounds

    def transform(self, matrix: Matrix4x4) -> 'Solid':
        """
        Aplica una transformación matricial al sólido.
        Retorna un *nuevo* Sólido transformado.

        Esta implementación difiere del snippet del README para
        correctamente transformar los 'bounds' (límites).
        """
        try:
            # La inversa es necesaria para mapear el punto de consulta
            # de vuelta al espacio original del objeto.
            inv_matrix = matrix.inverse()
        except ValueError:
            # Si la matriz no es invertible (ej. escala 0),
            # el sólido colapsa a nada.
            return Solid(lambda p: False, (Vector3(0,0,0), Vector3(0,0,0)))

        # Función 'contains' del nuevo sólido:
        def new_contains(point: Vector3) -> bool:
            # Transformar el punto de consulta al espacio original
            original_point = inv_matrix.apply_to_vector(point)
            # Comprobar si estaba contenido en el sólido original
            return self.contains(original_point)

        # Calcula el nuevo bounding box (AABB)
        new_bounds = transform_bounds(self.bounds, matrix)

        return Solid(new_contains, new_bounds)