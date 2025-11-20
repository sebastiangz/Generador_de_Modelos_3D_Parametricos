"""
Tests para el módulo src.curves (Curvas Paramétricas).
Verifica la lógica de los constructores de curvas (Bézier, B-spline, NURBS).
"""

import pytest
import math
import numpy as np
from dataclasses import dataclass
from typing import Callable, Tuple, List

# --- INICIO DE MOCKS (Simulaciones de tus dependencias) ---

@dataclass(frozen=True)
class Vector3:
    """Simulación mínima de Vector3 para que los tests funcionen."""
    x: float
    y: float
    z: float

    # Solo necesitamos las operaciones básicas para la fórmula de Bernstein y B-spline
    def __add__(self, other: 'Vector3') -> 'Vector3':
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __mul__(self, scalar: float) -> 'Vector3':
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __truediv__(self, scalar: float) -> 'Vector3':
        if scalar == 0: raise ValueError("División por cero")
        return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)
    
    def __eq__(self, other):
        """Permite la comparación usando pytest.approx para flotantes"""
        if not isinstance(other, Vector3):
            return False
        # Usar un alto grado de precisión (abs=1e-6) para coordenadas
        return (self.x == pytest.approx(other.x, abs=1e-6) and
                self.y == pytest.approx(other.y, abs=1e-6) and
                self.z == pytest.approx(other.z, abs=1e-6))

# --- FIN DE MOCKS ---


# --- Inyectar Mocks y Cargar el Código a Probar ---
import src.curves
src.curves.Vector3 = Vector3

# Importar las funciones que realmente queremos probar
from src.curves import cubic_bezier, b_spline_curve, nurbs_curve

# --- Puntos de Control Comunes ---
P0 = Vector3(0, 0, 0)
P1 = Vector3(10, 0, 0)
P2 = Vector3(10, 10, 0)
P3 = Vector3(0, 10, 0)


# --- INICIO DE LOS TESTS ---

### 1. Pruebas para cubic_bezier() ###

def test_bezier_start_end_points():
    """La curva debe empezar en P0 (t=0) y terminar en P3 (t=1)."""
    curve_fn = cubic_bezier(P0, P1, P2, P3)
    
    # Inicia en P0
    assert curve_fn(0.0) == P0
    # Termina en P3
    assert curve_fn(1.0) == P3

def test_bezier_midpoint():
    """Para una Bézier, el punto central (t=0.5) debe ser verificable."""
    curve_fn = cubic_bezier(P0, P1, P2, P3)
    
    # La fórmula en t=0.5 es 1/8 * P0 + 3/8 * P1 + 3/8 * P2 + 1/8 * P3
    # P0(0,0,0), P1(10,0,0), P2(10,10,0), P3(0,10,0)
    # X: (1/8)*0 + (3/8)*10 + (3/8)*10 + (1/8)*0 = 60/8 = 7.5
    # Y: (1/8)*0 + (3/8)*0 + (3/8)*10 + (1/8)*10 = 40/8 = 5.0
    expected = Vector3(7.5, 5.0, 0.0)
    assert curve_fn(0.5) == expected

def test_bezier_clamping():
    """Asegura que el parámetro 't' se recorta a [0, 1]."""
    curve_fn = cubic_bezier(P0, P1, P2, P3)
    # t < 0 debe dar P0
    assert curve_fn(-0.1) == P0
    # t > 1 debe dar P3
    assert curve_fn(1.1) == P3


### 2. Pruebas para b_spline_curve() ###

# Utiliza una configuración estándar de nodos (clamped/abierta)
# Grado 1 (lineal), 4 puntos de control
def setup_b_spline_linear():
    controls = [P0, P1, P2, P3]
    degree = 1
    # Nodos para curva abierta de grado 1: 0, 0, 1, 2, 3, 3
    knots = [0.0, 0.0, 1.0, 2.0, 3.0, 3.0] 
    return b_spline_curve(controls, knots, degree)

def test_bspline_start_end_points():
    """La B-Spline clamp debe tocar los puntos de control P0 y Pn."""
    curve_fn = setup_b_spline_linear()
    
    # El rango paramétrico es U[p] a U[n+1], que aquí es U[1] a U[4] -> [0.0, 3.0]
    # Inicia en P0
    assert curve_fn(0.0) == P0
    # Termina en P3
    assert curve_fn(3.0) == P3

def test_bspline_intermediate_point():
    """Prueba un punto intermedio conocido (t=1.0) para una B-Spline lineal."""
    curve_fn = setup_b_spline_linear()
    
    # En t=1.0, la curva debe estar exactamente en P1.
    # N1,1=1, N2,1=0, N3,1=0 (las bases son [1, 0, 0, 0])
    assert curve_fn(1.0) == P1

def test_bspline_mid_span_point():
    """Prueba un punto en el medio de un span (ej. t=0.5 en span 0-1)."""
    curve_fn = setup_b_spline_linear()
    
    # En t=0.5 (entre P0 y P1), debe ser el promedio: (P0 + P1) / 2
    expected = Vector3(5.0, 0.0, 0.0)
    assert curve_fn(0.5) == expected


### 3. Pruebas para nurbs_curve() ###

# Utiliza una configuración para modelar un CÍRCULO PERFECTO (caso canónico de NURBS)
def setup_nurbs_circle():
    # Puntos de control para un cuarto de círculo (Grado 2)
    # P0: (R, 0, 0), P1: (R, R, 0), P2: (0, R, 0)
    R = 10.0
    controls = [
        Vector3(R, 0, 0),
        Vector3(R, R, 0), 
        Vector3(0, R, 0)
    ]
    degree = 2
    
    # Nodos para un cuarto de círculo
    knots = [0, 0, 0, 1, 1, 1] 
    
    # Pesos (el peso en P1 debe ser cos(45) = sqrt(2)/2 ~= 0.707)
    weights = [1.0, math.sqrt(2)/2.0, 1.0]
    
    return nurbs_curve(controls, knots, weights, degree), R

def test_nurbs_circle_start_end_points():
    """La curva debe empezar y terminar en los puntos de control ponderados."""
    curve_fn, R = setup_nurbs_circle()
    
    # Inicia en P0 (t=0)
    assert curve_fn(0.0) == Vector3(R, 0, 0)
    # Termina en P2 (t=1)
    assert curve_fn(1.0) == Vector3(0, R, 0)

def test_nurbs_circle_midpoint_on_arc():
    """Prueba que el punto medio (t=0.5) está en el arco (distancia R del origen)."""
    curve_fn, R = setup_nurbs_circle()
    mid_point = curve_fn(0.5)
    
    # En el círculo, la distancia del punto al origen debe ser igual al radio R.
    # mid_point.magnitude() debe ser R
    assert (mid_point.x**2 + mid_point.y**2)**0.5 == pytest.approx(R, abs=1e-6)
    
    # Específicamente, en t=0.5 (ángulo de 45 grados)
    expected_val = R * math.cos(math.pi/4) # 10 * 0.707...
    expected_point = Vector3(expected_val, expected_val, 0)
    assert mid_point == expected_point

def test_nurbs_mismatched_weights():
    """Asegura que la NURBS lanza un error si los pesos no coinciden con los controles."""
    controls = [P0, P1]
    knots = [0, 0, 1, 1]
    weights = [1.0] # Solo un peso, pero dos puntos de control
    degree = 1
    
    with pytest.raises(ValueError, match="Debe haber un peso"):
        nurbs_curve(controls, knots, weights, degree)