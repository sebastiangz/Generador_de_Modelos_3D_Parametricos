import math
from typing import Callable
from algebra_lineal import (
    Malla,
    Vertice,
    calcular_bounding_box,
    extraer_vertices,
    norma,
    restar_vectores,
)

SDF = Callable[[Vertice], float]

def union(solido_a: SDF, solido_b: SDF) -> SDF:
    """Devuelve un nuevo sólido CSG que representa la unión A ∪ B."""
    return lambda p: min(solido_a(p), solido_b(p))

def intersection(solido_a: SDF, solido_b: SDF) -> SDF:
    """Devuelve un nuevo sólido CSG que representa la intersección A ∩ B."""
    return lambda p: max(solido_a(p), solido_b(p))

def difference(solido_a: SDF, solido_b: SDF) -> SDF:
    """Devuelve un nuevo sólido CSG que representa la diferencia A - B."""
    return lambda p: max(solido_a(p), -solido_b(p))

def sdf_caja(semi_dimensiones: Vertice) -> SDF:
    """SDF exacto de una caja centrada en el origen."""
    bx, by, bz = semi_dimensiones
    def evaluar(p: Vertice) -> float:
        qx = abs(p[0]) - bx
        qy = abs(p[1]) - by
        qz = abs(p[2]) - bz
        fuera = norma((max(qx, 0.0), max(qy, 0.0), max(qz, 0.0)))
        dentro = min(max(qx, max(qy, qz)), 0.0)
        return fuera + dentro
    return evaluar

def sdf_cilindro_z(radio: float, semi_largo: float) -> SDF:
    """SDF exacto de un cilindro alineado con el eje Z."""
    def evaluar(p: Vertice) -> float:
        dx = math.hypot(p[0], p[1]) - radio
        dz = abs(p[2]) - semi_largo
        fuera = math.hypot(max(dx, 0.0), max(dz, 0.0))
        dentro = min(max(dx, dz), 0.0)
        return fuera + dentro
    return evaluar

def malla_a_sdf(malla: Malla, resolucion_grid: int = 16) -> SDF:
    """
    Convierte una malla normalizada en [-1, 1]^3 en una función SDF pura
    mediante voxelización espacial por proximidad a los vértices/superficie.
    """
    vertices = extraer_vertices(malla)
    if not vertices:
        return lambda p: 1.0
    
    paso = max(1, len(vertices) // 800)
    muestra_vertices = vertices[::paso]
    radio_influencia = 2.2 / resolucion_grid

    v_min, v_max = calcular_bounding_box(malla)
    caja_envolvente = sdf_caja(
        (
            (v_max[0] - v_min[0]) / 2.0,
            (v_max[1] - v_min[1]) / 2.0,
            (v_max[2] - v_min[2]) / 2.0,
        )
    )

    def evaluar(p: Vertice) -> float:
        dist_caja = caja_envolvente(p)
        if dist_caja > radio_influencia:
            return dist_caja
        dist_min = min(norma(restar_vectores(p, v)) for v in muestra_vertices)
        return dist_min - radio_influencia

    return evaluar

def _generar_rejilla_puntos(resolucion: int = 14) -> tuple[Vertice, ...]:
    """Genera una nube de puntos determinista en el espacio normalizado [-1, 1]^3."""
    coordenadas = tuple(
        -1.0 + (2.0 * i) / (resolucion - 1)
        for i in range(resolucion)
    )
    return tuple(
        (x, y, z)
        for x in coordenadas
        for y in coordenadas
        for z in coordenadas
    )

def calcular_iou_csg(solido_a: SDF, solido_b: SDF, resolucion: int = 14) -> float:
    """
    Calcula el grado de coincidencia volumétrica (Índice de Jaccard / IoU 3D)
    usando las operaciones puras CSG intersection y union:
    IoU = Volumen(A ∩ B) / Volumen(A ∪ B)
    """
    puntos = _generar_rejilla_puntos(resolucion)
    solido_interseccion = intersection(solido_a, solido_b)
    solido_union = union(solido_a, solido_b)

    dentro_interseccion = sum(1 for p in puntos if solido_interseccion(p) <= 0.0)
    dentro_union = sum(1 for p in puntos if solido_union(p) <= 0.0)

    if dentro_union == 0:
        return 0.0
    return dentro_interseccion / dentro_union