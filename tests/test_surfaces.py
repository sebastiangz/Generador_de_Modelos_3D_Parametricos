"""
Tests para el módulo src.surfaces (Superficies Paramétricas).
"""

import pytest
import math
import numpy as np
from dataclasses import dataclass
from typing import Callable, Tuple

# --- INICIO DE MOCKS (Simulaciones de tus dependencias) ---

@dataclass(frozen=True)
class Vector3:
    """Simulación mínima de Vector3 para que los tests funcionen."""
    x: float
    y: float
    z: float

    def __eq__(self, other):
        """Permite la comparación usando pytest.approx para flotantes"""
        if not isinstance(other, Vector3):
            return False
        # Usar un alto grado de precisión (abs=1e-6) para coordenadas
        return (self.x == pytest.approx(other.x, abs=1e-6) and
                self.y == pytest.approx(other.y, abs=1e-6) and
                self.z == pytest.approx(other.z, abs=1e-6))

# Definición de tipos
Curve2D = Callable[[float], Tuple[float, float]]

# --- FIN DE MOCKS ---


# --- Inyectar Mocks y Cargar el Código a Probar ---
# (Esto le dice a tu módulo 'surfaces' que use nuestras clases simuladas)
import src.surfaces
src.surfaces.Vector3 = Vector3

# Importar las funciones que realmente queremos probar
from src.surfaces import surface_of_revolution


# --- DATOS DE PRUEBA (Arrange) ---

# Curva 2D de Perfil: (radio, altura)
# Perfil 1: Un cilindro de radio 10 y altura constante 5
def cylinder_profile(u: float) -> Tuple[float, float]:
    """Crea un perfil circular constante (cilindro)"""
    return (10.0, 5.0)

# Perfil 2: Un cono de radio 10 en la base (u=0) y radio 0 en la punta (u=1)
def cone_profile(u: float) -> Tuple[float, float]:
    """Crea un perfil lineal (cono)"""
    radio = 10.0 * (1.0 - u)
    altura = 10.0 * u - 5.0 # Altura de -5 a 5
    return (radio, altura)


# --- INICIO DE LOS TESTS ---

def test_surface_of_revolution_unimplemented_axis():
    """Prueba que un eje no implementado lanza un error."""
    with pytest.raises(NotImplementedError, match="solo está implementada para el eje 'z'"):
        surface_of_revolution(cylinder_profile, axis='x')

### 1. Pruebas para Cylinder Profile (Perfil Constante) ###

def test_surface_cylinder_start_point():
    """Prueba el punto inicial (u=0, v=0) - lado +X."""
    s = surface_of_revolution(cylinder_profile)
    # u=0: radio=10, z=5.0
    # v=0: ángulo 0 -> (x=10, y=0)
    assert s(0, 0) == Vector3(10.0, 0.0, 5.0)

def test_surface_cylinder_quarter_rotation():
    """Prueba el punto con rotación de 90 grados (v=0.25) - lado +Y."""
    s = surface_of_revolution(cylinder_profile)
    # v=0.25: ángulo 90 deg (pi/2) -> (x=0, y=10)
    assert s(0.5, 0.25) == Vector3(0.0, 10.0, 5.0)

def test_surface_cylinder_half_rotation():
    """Prueba el punto con rotación de 180 grados (v=0.5) - lado -X."""
    s = surface_of_revolution(cylinder_profile)
    # v=0.5: ángulo 180 deg (pi) -> (x=-10, y=0)
    assert s(1, 0.5) == Vector3(-10.0, 0.0, 5.0)

def test_surface_cylinder_full_rotation():
    """Prueba el punto con rotación completa (v=1.0) - debe ser igual a v=0."""
    s = surface_of_revolution(cylinder_profile)
    # v=1.0: ángulo 360 deg (2*pi) -> (x=10, y=0)
    assert s(0.0, 1.0) == Vector3(10.0, 0.0, 5.0)


### 2. Pruebas para Cone Profile (Perfil Variable) ###

def test_surface_cone_base():
    """Prueba un punto en la base del cono (u=0, z=-5)."""
    s = surface_of_revolution(cone_profile)
    # u=0: radio=10, z=-5.0 (Base)
    # v=0.75: rotación 270 deg (3*pi/2) -> (x=0, y=-10)
    assert s(0.0, 0.75) == Vector3(0.0, -10.0, -5.0)

def test_surface_cone_tip():
    """Prueba un punto en la punta del cono (u=1, z=5)."""
    s = surface_of_revolution(cone_profile)
    # u=1: radio=0, z=5.0 (Punta)
    # El punto debe ser el centro, sin importar v
    assert s(1.0, 0.25) == Vector3(0.0, 0.0, 5.0)

def test_surface_cone_midpoint():
    """Prueba un punto en el medio del cono (u=0.5, z=0)."""
    s = surface_of_revolution(cone_profile)
    # u=0.5: radio=5.0, z=0.0
    # v=0.0: ángulo 0 deg -> (x=5, y=0)
    assert s(0.5, 0.0) == Vector3(5.0, 0.0, 0.0)
    
def test_surface_cone_midpoint_rotated():
    """Prueba un punto en el medio del cono rotado (u=0.5, z=0)."""
    s = surface_of_revolution(cone_profile)
    # u=0.5: radio=5.0, z=0.0
    # v=0.5: ángulo 180 deg -> (x=-5, y=0)
    assert s(0.5, 0.5) == Vector3(-5.0, 0.0, 0.0)