import math
from functools import reduce
from typing import Callable
from algebra_lineal import (
    Malla,
    Matriz4x4,
    Vertice,
    aplicar_matriz_a_vertice,
    calcular_bounding_box,
    calcular_dimensiones,
    matriz_identidad,
    multiplicar_matrices,
)

Transformacion = Callable[[Vertice], Vertice]

# --- Composición Funcional ---

def compose(*funciones: Transformacion) -> Transformacion:
    """Combina múltiples funciones f(g(h(x))) en una sola función pura."""
    return reduce(
        lambda f, g: lambda x: f(g(x)),
        funciones,
        lambda x: x,
    )

def componer_matrices(*matrices: Matriz4x4) -> Matriz4x4:
    """Combina una secuencia de matrices 4x4 mediante multiplicación asociativa."""
    return reduce(multiplicar_matrices, matrices, matriz_identidad())

# --- Matrices Afines 4x4 ---

def matriz_traslacion(tx: float, ty: float, tz: float) -> Matriz4x4:
    return (
        (1.0, 0.0, 0.0, tx),
        (0.0, 1.0, 0.0, ty),
        (0.0, 0.0, 1.0, tz),
        (0.0, 0.0, 0.0, 1.0),
    )

def matriz_escalado(sx: float, sy: float, sz: float) -> Matriz4x4:
    return (
        (sx, 0.0, 0.0, 0.0),
        (0.0, sy, 0.0, 0.0),
        (0.0, 0.0, sz, 0.0),
        (0.0, 0.0, 0.0, 1.0),
    )

def matriz_rotacion_x(radianes: float) -> Matriz4x4:
    c, s = math.cos(radianes), math.sin(radianes)
    return (
        (1.0, 0.0, 0.0, 0.0),
        (0.0, c, -s, 0.0),
        (0.0, s, c, 0.0),
        (0.0, 0.0, 0.0, 1.0),
    )

def matriz_rotacion_y(radianes: float) -> Matriz4x4:
    c, s = math.cos(radianes), math.sin(radianes)
    return (
        (c, 0.0, s, 0.0),
        (0.0, 1.0, 0.0, 0.0),
        (-s, 0.0, c, 0.0),
        (0.0, 0.0, 0.0, 1.0),
    )

def matriz_rotacion_z(radianes: float) -> Matriz4x4:
    c, s = math.cos(radianes), math.sin(radianes)
    return (
        (c, -s, 0.0, 0.0),
        (s, c, 0.0, 0.0),
        (0.0, 0.0, 1.0, 0.0),
        (0.0, 0.0, 0.0, 1.0),
    )

# --- Aplicación a Mallas Inmutables ---

def aplicar_transformacion_malla(malla: Malla, fn: Transformacion) -> Malla:
    """Aplica una transformación pura a todos los vértices de una malla."""
    return tuple(
        (fn(v1), fn(v2), fn(v3))
        for (v1, v2, v3) in malla
    )

def _matriz_alineacion_eje_principal(malla: Malla) -> Matriz4x4:
    """
    Rota la malla en múltiplos de 90° para que su dimensión más larga
    siempre quede alineada con el eje Z (longitud) y la segunda con el eje Y (alto).
    """
    dx, dy, dz = calcular_dimensiones(malla)
    if dx >= dy and dx >= dz:
        # El eje más largo es X -> rotar 90° en Y para llevarlo a Z
        return matriz_rotacion_y(math.pi / 2.0)
    if dy >= dx and dy >= dz:
        # El eje más largo es Y -> rotar -90° en X para llevarlo a Z
        return matriz_rotacion_x(-math.pi / 2.0)
    return matriz_identidad()

def normalizar_malla(malla: Malla) -> Malla:
    """
    Pipeline composable de normalización:
    1. Centra la malla en (0, 0, 0) respecto a su Bounding Box.
    2. Alinea su eje principal con el eje Z.
    3. Escala uniformemente al rango [-1, 1].
    """
    if not malla:
        return malla

    v_min, v_max = calcular_bounding_box(malla)
    cx = (v_min[0] + v_max[0]) / 2.0
    cy = (v_min[1] + v_max[1]) / 2.0
    cz = (v_min[2] + v_max[2]) / 2.0

    # Paso 1 y 2: Centrar y alinear orientación
    m_centrar = matriz_traslacion(-cx, -cy, -cz)
    m_alinear = _matriz_alineacion_eje_principal(malla)
    m_pre = componer_matrices(m_alinear, m_centrar)

    malla_alineada = aplicar_transformacion_malla(
        malla, lambda v: aplicar_matriz_a_vertice(m_pre, v)
    )

    # Paso 3: Escalar uniformemente por su dimensión máxima para preservar proporciones
    dims = calcular_dimensiones(malla_alineada)
    max_dim = max(dims) if max(dims) > 0.0 else 1.0
    factor = 2.0 / max_dim  # Rango total de 2.0 (de -1.0 a 1.0)

    fn_escalar = lambda v: aplicar_matriz_a_vertice(
        matriz_escalado(factor, factor, factor), v
    )
    return aplicar_transformacion_malla(malla_alineada, fn_escalar)