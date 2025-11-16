"""
Archivo de test completo para el módulo src.csg.
Utiliza pytest para las verificaciones.
"""

import pytest
from dataclasses import dataclass
from typing import Callable, Tuple

# --- INICIO DE MOCKS (Simulaciones de tus clases) ---
# En tu código real, borrarías esta sección y harías:
# from src.vectors import Vector3, Matrix4x4

@dataclass(frozen=True)
class Vector3:
    """Simulación mínima de Vector3 para que los tests funcionen."""
    x: float
    y: float
    z: float

    def __eq__(self, other):
        if not isinstance(other, Vector3):
            return False
        # Usar pytest.approx para manejar errores de punto flotante
        return (self.x == pytest.approx(other.x) and
                self.y == pytest.approx(other.y) and
                self.z == pytest.approx(other.z))

class Matrix4x4:
    """
    Simulación mínima de Matrix4x4 para que los tests funcionen.
    Solo implementa las transformaciones que vamos a probar.
    """
    
    @staticmethod
    def identity():
        return Matrix4x4() # Una matriz "vacía" que representa la identidad

    @staticmethod
    def translation(tx, ty, tz):
        # Guardamos los valores de traslación para usarlos en 'apply'
        return Matrix4x4(trans=(tx, ty, tz))
    
    @staticmethod
    def scale(sx, sy, sz):
        # Guardamos la escala para 'inverse'
        return Matrix4x4(scale=(sx, sy, sz))

    def __init__(self, trans=None, scale=None):
        self.trans = trans or (0, 0, 0)
        self.scale = scale or (1, 1, 1)

    def inverse(self):
        """Calcula la inversa (solo para este mock)"""
        if self.scale[0] == 0 or self.scale[1] == 0 or self.scale[2] == 0:
            raise ValueError("Matrix is not invertible (mock)")
        
        # Inversa de traslación T(v) es T(-v)
        # (Ignoramos escala en la inversa de traslación para este simple mock)
        return Matrix4x4(trans=(-self.trans[0], -self.trans[1], -self.trans[2]))
        
    def apply_to_vector(self, v: Vector3) -> Vector3:
        """Aplica la transformación (solo para este mock)"""
        # Solo aplica la traslación definida
        return Vector3(
            v.x + self.trans[0],
            v.y + self.trans[1],
            v.z + self.trans[2]
        )

# --- FIN DE MOCKS ---


# --- Importamos el código REAL que queremos probar ---
# (Asumimos que tu código está en src/csg.py y src/vectors.py)
# y que este test corre desde la raíz del proyecto.
from src.csg import (
    combine_bounds,
    intersect_bounds,
    transform_bounds,
    Solid,
    union,
    intersection,
    difference
)
# Sobrescribimos las importaciones de 'csg' para que usen nuestros Mocks
import src.csg
src.csg.Vector3 = Vector3
src.csg.Matrix4x4 = Matrix4x4


# --- DATOS DE PRUEBA (Arrange) ---

VEC_ZERO = Vector3(0, 0, 0)
VEC_ONES = Vector3(1, 1, 1)

# Un cubo de 1x1x1 en el origen
BOX_UNIT = (Vector3(0, 0, 0), Vector3(1, 1, 1))
# Un cubo de 1x1x1 desplazado, que se solapa
BOX_OFFSET = (Vector3(0.5, 0.5, 0.5), Vector3(1.5, 1.5, 1.5))
# Un cubo lejano, que no se solapa
BOX_FAR = (Vector3(10, 10, 10), Vector3(11, 11, 11))
# Un cubo "dentro" del cubo unidad
BOX_INNER = (Vector3(0.2, 0.2, 0.2), Vector3(0.8, 0.8, 0.8))

# Sólidos primitivos para probar operaciones
def cube_contains(p: Vector3) -> bool:
    return 0 <= p.x <= 1 and 0 <= p.y <= 1 and 0 <= p.z <= 1
SOLID_CUBE_1 = Solid(cube_contains, BOX_UNIT)

def offset_cube_contains(p: Vector3) -> bool:
    return 0.5 <= p.x <= 1.5 and 0.5 <= p.y <= 1.5 and 0.5 <= p.z <= 1.5
SOLID_CUBE_2 = Solid(offset_cube_contains, BOX_OFFSET)


# --- INICIO DE LOS TESTS ---

### 1. Pruebas para Funciones Auxiliares (Bounds) ###

def test_combine_bounds_overlapping():
    """Prueba (Happy Path): Combinación de dos cajas que se solapan."""
    result_bounds = combine_bounds(BOX_UNIT, BOX_OFFSET)
    
    # El mínimo debe ser (0, 0, 0) y el máximo (1.5, 1.5, 1.5)
    assert result_bounds[0] == Vector3(0, 0, 0)
    assert result_bounds[1] == Vector3(1.5, 1.5, 1.5)

def test_combine_bounds_one_inside_other():
    """Prueba (Edge Case): Combinar una caja contenida en otra."""
    result_bounds = combine_bounds(BOX_UNIT, BOX_INNER)
    # El resultado debe ser la caja exterior (BOX_UNIT)
    assert result_bounds == BOX_UNIT

def test_intersect_bounds_overlapping():
    """Prueba (Happy Path): Intersección de dos cajas que se solapan."""
    result_bounds = intersect_bounds(BOX_UNIT, BOX_OFFSET)
    
    # El mínimo debe ser (0.5, 0.5, 0.5) y el máximo (1, 1, 1)
    assert result_bounds[0] == Vector3(0.5, 0.5, 0.5)
    assert result_bounds[1] == Vector3(1, 1, 1)

def test_intersect_bounds_no_overlap():
    """Prueba (Edge Case): Intersección de dos cajas que no se tocan."""
    result_bounds = intersect_bounds(BOX_UNIT, BOX_FAR)
    
    # Debe retornar la caja "vacía" (colapsada en el origen)
    assert result_bounds[0] == VEC_ZERO
    assert result_bounds[1] == VEC_ZERO

def test_transform_bounds_identity():
    """Prueba (Happy Path): Transformar con matriz identidad no cambia nada."""
    matrix_id = Matrix4x4.identity()
    new_bounds = transform_bounds(BOX_UNIT, matrix_id)
    assert new_bounds == BOX_UNIT

def test_transform_bounds_translation():
    """Prueba (Happy Path): Una traslación simple mueve los límites."""
    # Mover todo 10 unidades en X
    matrix_trans = Matrix4x4.translation(10, 0, 0)
    new_bounds = transform_bounds(BOX_UNIT, matrix_trans)
    
    # La caja original (0,0,0)-(1,1,1) ahora debe ser (10,0,0)-(11,1,1)
    assert new_bounds[0] == Vector3(10, 0, 0)
    assert new_bounds[1] == Vector3(11, 1, 1)

### 2. Pruebas para la Clase Solid ###

def test_solid_transform_translation():
    """Prueba (Happy Path): Un sólido trasladado contiene los puntos correctos."""
    matrix_trans = Matrix4x4.translation(10, 0, 0)
    
    # Act: Trasladamos nuestro cubo unidad
    translated_cube = SOLID_CUBE_1.transform(matrix_trans)
    
    # Assert 1: El Bounding Box debe ser correcto
    assert translated_cube.bounds == (Vector3(10, 0, 0), Vector3(11, 1, 1))
    
    # Assert 2: La función 'contains' debe usar la matriz inversa
    
    # Un punto en el espacio original ya NO debe estar
    assert not translated_cube.contains(Vector3(0.5, 0.5, 0.5))
    
    # El mismo punto en el espacio *nuevo* (trasladado) SÍ debe estar
    assert translated_cube.contains(Vector3(10.5, 0.5, 0.5))
    
    # Un punto lejano no debe estar
    assert not translated_cube.contains(Vector3(100, 100, 100))

def test_solid_transform_non_invertible():
    """Prueba (Error Case): Matriz no invertible (escala 0) colapsa el sólido."""
    matrix_zero_scale = Matrix4x4.scale(0, 0, 0) 
    
    # Act: Transformamos con la matriz singular
    collapsed_solid = SOLID_CUBE_1.transform(matrix_zero_scale)
    
    # Assert: Debe devolver un sólido vacío
    assert collapsed_solid.bounds == (VEC_ZERO, VEC_ZERO)
    assert not collapsed_solid.contains(Vector3(0, 0, 0))
    assert not collapsed_solid.contains(Vector3(0.5, 0.5, 0.5))

### 3. Pruebas para Operaciones CSG ###

# Puntos de prueba para CSG
P_SOLO_EN_1 = Vector3(0.1, 0.1, 0.1)
P_SOLO_EN_2 = Vector3(1.1, 1.1, 1.1)
P_EN_AMBOS = Vector3(0.7, 0.7, 0.7)
P_EN_NINGUNO = Vector3(10, 10, 10)

def test_union_cases():
    """Prueba la lógica 'OR' de la Unión."""
    u = union(SOLID_CUBE_1, SOLID_CUBE_2)
    
    assert u.contains(P_SOLO_EN_1) == True
    assert u.contains(P_SOLO_EN_2) == True
    assert u.contains(P_EN_AMBOS) == True
    assert u.contains(P_EN_NINGUNO) == False
    
    # Verificar que el bounds es la combinación
    assert u.bounds == combine_bounds(SOLID_CUBE_1.bounds, SOLID_CUBE_2.bounds)

def test_intersection_cases():
    """Prueba la lógica 'AND' de la Intersección."""
    i = intersection(SOLID_CUBE_1, SOLID_CUBE_2)
    
    assert i.contains(P_SOLO_EN_1) == False
    assert i.contains(P_SOLO_EN_2) == False
    assert i.contains(P_EN_AMBOS) == True
    assert i.contains(P_EN_NINGUNO) == False
    
    # Verificar que el bounds es la intersección
    assert i.bounds == intersect_bounds(SOLID_CUBE_1.bounds, SOLID_CUBE_2.bounds)

def test_difference_cases():
    """Prueba la lógica 'AND NOT' de la Diferencia (S1 - S2)."""
    d = difference(SOLID_CUBE_1, SOLID_CUBE_2)
    
    # Punto solo en S1 (Debe estar)
    assert d.contains(P_SOLO_EN_1) == True
    # Punto solo en S2 (No está en S1, así que False)
    assert d.contains(P_SOLO_EN_2) == False
    # Punto en AMBOS (Está en S1, PERO también en S2 -> False)
    assert d.contains(P_EN_AMBOS) == False
    # Punto en NINGUNO (False)
    assert d.contains(P_EN_NINGUNO) == False
    
    # Verificar que el bounds es el del primer sólido
    assert d.bounds == SOLID_CUBE_1.bounds