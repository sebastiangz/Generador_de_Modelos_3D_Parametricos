"""
Tests para el módulo src.geometry (Primitivas Geométricas).
"""

import pytest
import math
from dataclasses import dataclass
from typing import Callable, Tuple

# --- INICIO DE MOCKS (Simulaciones de tus dependencias) ---
# (Asumimos que Vector3 y Solid vienen de otros módulos)

@dataclass(frozen=True)
class Vector3:
    """Simulación mínima de Vector3 para que los tests funcionen."""
    x: float
    y: float
    z: float

    def magnitude(self) -> float:
        """Calcula la magnitud (distancia desde el origen)"""
        return (self.x**2 + self.y**2 + self.z**2)**0.5
    
    def __eq__(self, other):
        """Permite la comparación usando pytest.approx para flotantes"""
        if not isinstance(other, Vector3):
            return False
        return (self.x == pytest.approx(other.x) and
                self.y == pytest.approx(other.y) and
                self.z == pytest.approx(other.z))

# Definición de tipos
Bounds = Tuple[Vector3, Vector3]

@dataclass(frozen=True)
class Solid:
    """Simulación mínima de la clase Solid."""
    contains: Callable[[Vector3], bool]
    bounds: Bounds

# --- FIN DE MOCKS ---


# --- Inyectar Mocks y Cargar el Código a Probar ---
# (Esto le dice a tu módulo 'geometry' que use nuestras clases simuladas)
import src.geometry
src.geometry.Vector3 = Vector3
src.geometry.Solid = Solid
src.geometry.Bounds = Bounds

# Importar las funciones que realmente queremos probar
from src.geometry import sphere, box, cylinder, cone, torus, pyramid


# --- Puntos de Prueba Comunes ---
ORIGIN = Vector3(0, 0, 0)

# --- Tests para sphere() ---

def test_sphere_invalid_radius():
    """Prueba que la esfera lanza un error si el radio no es positivo."""
    with pytest.raises(ValueError, match="El radio debe ser positivo"):
        sphere(0)
    with pytest.raises(ValueError, match="El radio debe ser positivo"):
        sphere(-10)

def test_sphere_contains():
    """Prueba la lógica 'contains' de la esfera."""
    s = sphere(radius=10)
    
    # Dentro
    assert s.contains(ORIGIN) is True
    assert s.contains(Vector3(5, 0, 0)) is True
    # En el borde
    assert s.contains(Vector3(10, 0, 0)) is True
    # Fuera
    assert s.contains(Vector3(10.1, 0, 0)) is False
    assert s.contains(Vector3(5, 5, 8)) is False # (25+25+64 > 100)

def test_sphere_bounds():
    """Prueba los límites (bounds) de la esfera."""
    s = sphere(radius=10)
    assert s.bounds[0] == Vector3(-10, -10, -10)
    assert s.bounds[1] == Vector3(10, 10, 10)


# --- Tests para box() ---

def test_box_invalid_dimensions():
    """Prueba que la caja lanza un error si alguna dimensión no es positiva."""
    with pytest.raises(ValueError, match="Las dimensiones deben ser positivas"):
        box(1, 1, 0)
    with pytest.raises(ValueError, match="Las dimensiones deben ser positivas"):
        box(1, -1, 1)

def test_box_contains():
    """Prueba la lógica 'contains' de la caja."""
    b = box(width=10, height=20, depth=30) # w2=5, h2=10, d2=15
    
    # Dentro
    assert b.contains(ORIGIN) is True
    assert b.contains(Vector3(4, 9, 14)) is True
    # En el borde
    assert b.contains(Vector3(5, 10, 15)) is True
    assert b.contains(Vector3(-5, -10, -15)) is True
    # Fuera
    assert b.contains(Vector3(5.1, 0, 0)) is False
    assert b.contains(Vector3(0, 10.1, 0)) is False
    assert b.contains(Vector3(0, 0, 15.1)) is False

def test_box_bounds():
    """Prueba los límites (bounds) de la caja."""
    b = box(width=10, height=20, depth=30)
    assert b.bounds[0] == Vector3(-5, -10, -15)
    assert b.bounds[1] == Vector3(5, 10, 15)


# --- Tests para cylinder() ---

def test_cylinder_invalid_dimensions():
    """Prueba que el cilindro lanza un error si las dimensiones no son positivas."""
    with pytest.raises(ValueError, match="El radio y la altura deben ser positivos"):
        cylinder(1, 0)
    with pytest.raises(ValueError, match="El radio y la altura deben ser positivos"):
        cylinder(-1, 1)

def test_cylinder_contains():
    """Prueba la lógica 'contains' del cilindro."""
    c = cylinder(radius=5, height=20) # r=5, h2=10
    
    # Dentro
    assert c.contains(ORIGIN) is True
    assert c.contains(Vector3(3, 3, 9)) is True
    # En el borde (radio y altura)
    assert c.contains(Vector3(5, 0, 10)) is True
    # Fuera (por radio)
    assert c.contains(Vector3(5.1, 0, 5)) is False
    # Fuera (por altura)
    assert c.contains(Vector3(3, 3, 10.1)) is False

def test_cylinder_bounds():
    """Prueba los límites (bounds) del cilindro."""
    c = cylinder(radius=5, height=20)
    assert c.bounds[0] == Vector3(-5, -5, -10)
    assert c.bounds[1] == Vector3(5, 5, 10)


# --- Tests para cone() ---

def test_cone_invalid_dimensions():
    """Prueba que el cono lanza un error si las dimensiones no son positivas."""
    with pytest.raises(ValueError, match="El radio y la altura deben ser positivos"):
        cone(1, 0)

def test_cone_contains():
    """Prueba la lógica 'contains' del cono (interpolación lineal)."""
    c = cone(radius=10, height=20) # r=10, h2=10
    
    # Fuera (por altura)
    assert c.contains(Vector3(0, 0, 10.1)) is False
    
    # En la punta (z = +h2 = 10). Radio debe ser 0.
    assert c.contains(Vector3(0, 0, 10)) is True
    assert c.contains(Vector3(0.1, 0, 10)) is False
    
    # En el centro (z = 0). Radio debe ser r/2 = 5.
    assert c.contains(Vector3(0, 0, 0)) is True
    assert c.contains(Vector3(5, 0, 0)) is True
    assert c.contains(Vector3(5.1, 0, 0)) is False
    
    # En la base (z = -h2 = -10). Radio debe ser r = 10.
    assert c.contains(Vector3(10, 0, -10)) is True
    assert c.contains(Vector3(10.1, 0, -10)) is False

def test_cone_bounds():
    """Prueba los límites (bounds) del cono."""
    c = cone(radius=10, height=20)
    assert c.bounds[0] == Vector3(-10, -10, -10)
    assert c.bounds[1] == Vector3(10, 10, 10)


# --- Tests para torus() ---

def test_torus_invalid_dimensions():
    """Prueba que el toro lanza un error si los radios no son positivos."""
    with pytest.raises(ValueError, match="Los radios deben ser positivos"):
        torus(1, 0)
    with pytest.raises(ValueError, match="Los radios deben ser positivos"):
        torus(-1, 1)

def test_torus_contains():
    """Prueba la lógica 'contains' del toro."""
    t = torus(major_radius=10, minor_radius=2) # R=10, r=2
    
    # En el "agujero" (fuera)
    assert t.contains(ORIGIN) is False
    assert t.contains(Vector3(5, 0, 0)) is False # (5-10)^2 + 0 = 25. Falla.
    
    # En el centro del "tubo" (dentro)
    assert t.contains(Vector3(10, 0, 0)) is True # (10-10)^2 + 0 = 0. Pasa.
    
    # En los bordes (dentro, en la superficie)
    assert t.contains(Vector3(8, 0, 0)) is True    # Borde interior (8-10)^2 = 4. Pasa.
    assert t.contains(Vector3(12, 0, 0)) is True  # Borde exterior (12-10)^2 = 4. Pasa.
    assert t.contains(Vector3(10, 0, 2)) is True  # Borde superior (10-10)^2 + 2^2 = 4. Pasa.
    
    # Fuera
    assert t.contains(Vector3(10, 0, 2.1)) is False # (10-10)^2 + 2.1^2 > 4
    assert t.contains(Vector3(12.1, 0, 0)) is False # (12.1-10)^2 > 4

def test_torus_bounds():
    """Prueba los límites (bounds) del toro."""
    t = torus(major_radius=10, minor_radius=2)
    R, r = 10, 2
    assert t.bounds[0] == Vector3(-R - r, -R - r, -r)
    assert t.bounds[1] == Vector3(R + r, R + r, r)


# --- Tests para pyramid() ---

def test_pyramid_invalid_dimensions():
    """Prueba que la pirámide lanza un error si las dimensiones no son positivas."""
    with pytest.raises(ValueError, match="Las dimensiones deben ser positivas"):
        pyramid(1, 1, 0)

def test_pyramid_contains():
    """Prueba la lógica 'contains' de la pirámide (interpolación)."""
    p = pyramid(width=10, depth=20, height=30) # w2=5, d2=10, h2=15
    
    # En la punta (z = +h2 = 15). Dimensiones deben ser 0.
    assert p.contains(Vector3(0, 0, 15)) is True
    assert p.contains(Vector3(0.1, 0, 15)) is False
    
    # En el centro (z = 0). Dimensiones deben ser w2/2=2.5, d2/2=5
    assert p.contains(Vector3(2.5, 5, 0)) is True
    assert p.contains(Vector3(2.6, 5, 0)) is False
    assert p.contains(Vector3(2.5, 5.1, 0)) is False
    
    # En la base (z = -h2 = -15). Dimensiones deben ser w2=5, d2=10
    assert p.contains(Vector3(5, 10, -15)) is True
    assert p.contains(Vector3(5.1, 10, -15)) is False

def test_pyramid_bounds():
    """Prueba los límites (bounds) de la pirámide."""
    p = pyramid(width=10, depth=20, height=30)
    assert p.bounds[0] == Vector3(-5, -10, -15)
    assert p.bounds[1] == Vector3(5, 10, 15)