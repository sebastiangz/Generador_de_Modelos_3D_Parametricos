"""
Tests para el módulo src.transforms (Funciones de Transformación).

Este archivo prueba el patrón de "higher-order function" usando 'mocker'
para "parchear" (patch) las funciones privadas que generan matrices.
"""

import pytest
from unittest.mock import MagicMock

# Importamos la clase real para usarla como 'spec'
from src.csg import Solid

# Importamos las funciones públicas que queremos probar
from src.transforms import (
    translate,
    scale,
    scale_uniform,
    rotate,
    reflect,
    shear,
    rotate_by_quaternion
)

# --- Fixtures de Pytest ---

@pytest.fixture
def mock_solid() -> MagicMock:
    """Simula un objeto Solid."""
    return MagicMock(spec=Solid)

@pytest.fixture
def mock_matrix() -> str:
    """Simula un objeto Matrix4x4."""
    return "--- MOCK_MATRIX_OBJ ---"


# --- Pruebas de las Funciones Públicas ---

def test_translate(mocker, mock_solid, mock_matrix):
    """Prueba que translate() usa la matriz de traslación correcta."""
    mock_creator = mocker.patch(
        'src.transforms._translation_matrix', 
        return_value=mock_matrix
    )
    
    transform_fn = translate(10, 20, 30)
    result_solid = transform_fn(mock_solid)
    
    mock_creator.assert_called_once_with(10, 20, 30)
    mock_solid.transform.assert_called_once_with(mock_matrix)
    assert result_solid == mock_solid.transform.return_value

def test_scale(mocker, mock_solid, mock_matrix):
    """Prueba que scale() usa la matriz de escala correcta."""
    mock_creator = mocker.patch(
        'src.transforms._scale_matrix', 
        return_value=mock_matrix
    )
    
    transform_fn = scale(2, 3, 4)
    transform_fn(mock_solid)
    
    mock_creator.assert_called_once_with(2, 3, 4)
    mock_solid.transform.assert_called_once_with(mock_matrix)

def test_scale_uniform(mocker, mock_solid, mock_matrix):
    """Prueba que scale_uniform() llama a _scale_matrix correctamente."""
    mock_creator = mocker.patch(
        'src.transforms._scale_matrix', 
        return_value=mock_matrix
    )
    
    transform_fn = scale_uniform(5)
    transform_fn(mock_solid)
    
    mock_creator.assert_called_once_with(5, 5, 5)
    mock_solid.transform.assert_called_once_with(mock_matrix)

def test_rotate(mocker, mock_solid, mock_matrix):
    """Prueba que rotate() usa la matriz de rotación correcta."""
    mock_creator = mocker.patch(
        'src.transforms._rotation_matrix', 
        return_value=mock_matrix
    )
    
    transform_fn = rotate('x', 90)
    transform_fn(mock_solid)
    
    mock_creator.assert_called_once_with('x', 90)
    mock_solid.transform.assert_called_once_with(mock_matrix)

def test_reflect(mocker, mock_solid, mock_matrix):
    """Prueba que reflect() usa la matriz de reflexión correcta."""
    mock_creator = mocker.patch(
        'src.transforms._reflection_matrix', 
        return_value=mock_matrix
    )
    
    transform_fn = reflect('xy')
    transform_fn(mock_solid)
    
    mock_creator.assert_called_once_with('xy')
    mock_solid.transform.assert_called_once_with(mock_matrix)

def test_shear(mocker, mock_solid, mock_matrix):
    """Prueba que shear() usa la matriz de cizallamiento correcta."""
    mock_creator = mocker.patch(
        'src.transforms._shear_matrix', 
        return_value=mock_matrix
    )
    
    # Llamamos a la función pública 'shear'
    transform_fn = shear(xy=1.5, zx=0.5)
    transform_fn(mock_solid)
    
    # Tu código 'src/transforms.py' llama al helper _shear_matrix
    # usando argumentos POSICIONALES, no nombrados.
    mock_creator.assert_called_once_with(
        1.5, 0, 0, 0, 0.5, 0
    )
    
    # Verificamos que el sólido fue transformado con esa matriz
    mock_solid.transform.assert_called_once_with(mock_matrix)

def test_rotate_by_quaternion(mocker, mock_solid, mock_matrix):
    """Prueba que rotate_by_quaternion() usa la matriz de quaternion correcta."""
    mock_creator = mocker.patch(
        'src.transforms._rotation_from_quaternion', 
        return_value=mock_matrix
    )
    
    q_tuple = (0.707, 0, 0.707, 0) # (w, x, y, z)
    transform_fn = rotate_by_quaternion(q_tuple)
    transform_fn(mock_solid)
    
    mock_creator.assert_called_once_with(q_tuple)
    mock_solid.transform.assert_called_once_with(mock_matrix)


# --- Pruebas de Errores en Helpers Privados ---

from src.transforms import _rotation_matrix, _reflection_matrix

def test_rotation_matrix_invalid_axis():
    """Prueba que _rotation_matrix lanza un error con un eje inválido."""
    with pytest.raises(ValueError, match="El eje de rotación debe ser"):
        _rotation_matrix(axis='w', degrees=90)

def test_reflection_matrix_invalid_plane():
    """Prueba que _reflection_matrix lanza un error con un plano inválido."""
    with pytest.raises(ValueError, match="El plano de reflexión debe ser"):
        _reflection_matrix(axis='xx')