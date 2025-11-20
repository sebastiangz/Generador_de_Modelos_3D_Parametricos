import pytest
from dataclasses import FrozenInstanceError
from src.vectors import Vector3, Matrix4x4

# ==========================================
# TESTEOS PARA VECTOR3
# ==========================================

def test_vector3_initialization():
    """Prueba la creacion basica e inmutabilidad."""
    v = Vector3(1.0, 2.0, 3.0)
    assert v.x == 1.0
    assert v.y == 2.0
    assert v.z == 3.0

    with pytest.raises(FrozenInstanceError):
        v.x = 5.0

def test_vector3_arithmetic():
    """Prueba suma, resta, multiplicacion y division escalar."""
    v1 = Vector3(1, 2, 3)
    v2 = Vector3(4, 5, 6)

    assert v1 + v2 == Vector3(5, 7, 9)
    assert v2 - v1 == Vector3(3, 3, 3)
    assert v1 * 2 == Vector3(2, 4, 6)
    assert v2 / 2 == Vector3(2.0, 2.5, 3.0)

def test_vector3_division_by_zero():
    """Prueba que lance error al dividir por cero."""
    v = Vector3(1, 2, 3)
    with pytest.raises(ValueError, match="No se puede dividir"):
        _ = v / 0

def test_vector3_dot_product():
    """Prueba producto punto (escalar)."""
    v1 = Vector3(1, 0, 0)
    v2 = Vector3(0, 1, 0)
    assert v1.dot(v2) == 0.0

    v3 = Vector3(1, 2, 3)
    assert v3.dot(v3) == 14.0

def test_vector3_cross_product():
    """Prueba producto cruz (vector perpendicular)."""
    x_axis = Vector3(1, 0, 0)
    y_axis = Vector3(0, 1, 0)
    
    z_axis = x_axis.cross(y_axis)
    assert z_axis == Vector3(0, 0, 1)

    neg_z = y_axis.cross(x_axis)
    assert neg_z == Vector3(0, 0, -1)

def test_vector3_magnitude_and_normalize():
    """Prueba longitud y normalizacion."""
    v = Vector3(3, 0, 4)
    assert v.magnitude() == 5.0

    v_norm = v.normalize()
    assert v_norm.magnitude() == pytest.approx(1.0)
    assert v_norm.x == pytest.approx(0.6)
    assert v_norm.z == pytest.approx(0.8)

def test_vector3_normalize_zero():
    """Normalizar vector cero debe retornar vector cero (safe)."""
    zero = Vector3(0, 0, 0)
    assert zero.normalize() == Vector3(0, 0, 0)

def test_vector3_map():
    """Prueba la funcion de orden superior map."""
    v = Vector3(-2, 3, -4)
    abs_v = v.map(abs)
    assert abs_v == Vector3(2, 3, 4)

# ==========================================
# TESTEOS PARA MATRIX4x4
# ==========================================

def test_matrix4x4_identity():
    """Prueba la matriz identidad."""
    ident = Matrix4x4.identity()
    v = Vector3(10, 20, 30)
    
    transformed = ident.apply_to_vector(v)
    assert transformed == v

def test_matrix4x4_initialization_check():
    """Debe fallar si no pasamos 16 elementos."""
    with pytest.raises(ValueError):
        Matrix4x4((1, 2, 3)) 

def test_matrix4x4_translation():
    """Prueba manual de una matriz de traslacion."""
    translation_data = (
        1, 0, 0, 5,
        0, 1, 0, 0,
        0, 0, 1, -2,
        0, 0, 0, 1
    )
    mat = Matrix4x4(translation_data)
    point = Vector3(1, 1, 1)
    
    result = mat.apply_to_vector(point)
    assert result == Vector3(6, 1, -1)

def test_matrix4x4_multiplication():
    """Prueba multiplicacion de matrices (Combinacion de transformaciones)."""
    scale = Matrix4x4((
        2, 0, 0, 0,
        0, 2, 0, 0,
        0, 0, 2, 0,
        0, 0, 0, 1
    ))
    
    translate = Matrix4x4((
        1, 0, 0, 10,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1
    ))

    combined = translate.multiply(scale)
    
    v = Vector3(1, 0, 0)
    result = combined.apply_to_vector(v)
    
    assert result.x == 12.0

def test_matrix4x4_inverse():
    """Prueba que la inversa deshaga una transformacion."""
    trans_data = (
        1, 0, 0, 5,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1
    )
    mat = Matrix4x4(trans_data)
    inv = mat.inverse()
    
    v = Vector3(10, 10, 10)
    
    moved = mat.apply_to_vector(v)       
    returned = inv.apply_to_vector(moved) 
    
    assert returned.x == pytest.approx(v.x)
    assert returned.y == pytest.approx(v.y)
    assert returned.z == pytest.approx(v.z)

def test_matrix4x4_non_invertible():
    """Prueba manejo de error con matrices singulares."""
    zero_scale = Matrix4x4((
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 1
    ))
    
    with pytest.raises(ValueError, match="no es invertible"):
        zero_scale.inverse()