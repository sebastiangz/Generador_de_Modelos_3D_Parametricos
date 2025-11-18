"""
src.curves
Define funciones para crear curvas paramétricas.
Cumple con: Bézier, B-splines, NURBS.
"""

from typing import Callable, List
import numpy as np
# Importa tu clase Vector3 desde tu archivo
from .vectors import Vector3

# Tipo para una curva paramétrica: (float) -> Vector3
ParametricCurve = Callable[[float], Vector3]

# --- Algoritmos Base para B-Spline / NURBS ---

def find_knot_span(n: int, p: int, u: float, U: np.ndarray) -> int:
    """
    Encuentra el índice del 'span' (intervalo) de nodos para el parámetro u.
    n: número de puntos de control - 1
    p: grado de la curva
    u: parámetro (0 a 1)
    U: vector de nodos
    """
    # Búsqueda binaria para encontrar el span
    span = np.searchsorted(U, u, side='right') - 1

    # Asegurarse de que el span esté dentro del rango válido
    return max(p, min(span, n))

def b_spline_basis(i: int, p: int, u: float, U: np.ndarray) -> List[float]:
    """
    Calcula las funciones base B-spline no nulas (algoritmo de Cox-de Boor).
    i: índice del span (de find_knot_span)
    p: grado
    u: parámetro
    U: vector de nodos
    Retorna una lista de p+1 valores de base.
    """
    N = np.zeros(p + 1)
    N[0] = 1.0

    left = np.zeros(p + 1)
    right = np.zeros(p + 1)

    for j in range(1, p + 1):
        left[j] = u - U[i + 1 - j]
        right[j] = U[i + j] - u
        saved = 0.0

        for r in range(j):
            temp = N[r] / (right[r + 1] + left[j - r])
            N[r] = saved + right[r + 1] * temp
            saved = left[j - r] * temp

        N[j] = saved

    return N

# --- Constructores de Curvas ---

def cubic_bezier(
    p0: Vector3,
    p1: Vector3, # Punto de control 1
    p2: Vector3, # Punto de control 2
    p3: Vector3
) -> ParametricCurve:
    """
    ✅ Crea una curva de Bézier cúbica.
    (Basado en tu código original, compatible con tu Vector3)
    `t` debe estar en el rango [0, 1].
    """
    def curve(t: float) -> Vector3:
        if not (0 <= t <= 1):
            t = max(0, min(1, t))

        omt = 1.0 - t
        omt2 = omt * omt
        omt3 = omt2 * omt
        t2 = t * t
        t3 = t2 * t

        # Fórmula de Bernstein. Esto funciona porque tu Vector3
        # define __mul__ (para vector * escalar) y __add__
        return (
            (p0 * omt3) +
            (p1 * (3 * omt2 * t)) +
            (p2 * (3 * omt * t2)) +
            (p3 * t3)
        )
    return curve

def b_spline_curve(
    controls: List[Vector3],
    knots: List[float],
    degree: int
) -> ParametricCurve:
    """
    ✅ Crea una curva B-spline.
    """
    n = len(controls) - 1
    p = degree
    U = np.array(knots)

    def curve(t: float) -> Vector3:
        # Asegurar que t esté en el rango válido de los nodos
        t_min = U[p]
        t_max = U[n + 1]
        t = max(t_min, min(t_max, t))

        # Encontrar el span de nodos y calcular las bases
        span_i = find_knot_span(n, p, t, U)
        basis = b_spline_basis(span_i, p, t, U)

        # Calcular el punto de la curva
        # Inicia con un Vector3 cero
        C = Vector3(0, 0, 0)
        for k in range(p + 1):
            # C += (Vector3 * float)
            # Esto es C = C + (Vector3 * float), que funciona
            # perfectamente con tu clase inmutable.
            C += controls[span_i - p + k] * basis[k]

        return C

    return curve

def nurbs_curve(
    controls: List[Vector3],
    knots: List[float],
    weights: List[float],
    degree: int
) -> ParametricCurve:
    """
    ✅ Crea una curva NURBS básica (Non-Uniform Rational B-Spline).
    """
    n = len(controls) - 1
    p = degree
    U = np.array(knots)

    if len(weights) != len(controls):
        raise ValueError("Debe haber un peso (weight) por cada punto de control")

    def curve(t: float) -> Vector3:
        # Asegurar que t esté en el rango válido de los nodos
        t_min = U[p]
        t_max = U[n + 1]
        t = max(t_min, min(t_max, t))

        # Encontrar el span de nodos y calcular las bases
        span_i = find_knot_span(n, p, t, U)
        basis = b_spline_basis(span_i, p, t, U)

        # Calcular el punto de la curva (forma racional)
        numerator = Vector3(0, 0, 0)
        denominator = 0.0

        for k in range(p + 1):
            idx = span_i - p + k
            weighted_basis = basis[k] * weights[idx]

            # numerator = numerator + (Vector3 * float)
            numerator += controls[idx] * weighted_basis
            denominator += weighted_basis

        if denominator == 0:
            return Vector3(0, 0, 0)

        # return Vector3 / float (usa __truediv__)
        return numerator / denominator

    return curve