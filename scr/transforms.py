"""
src.transforms
Define las funciones de transformación 3D composables.

Este módulo implementa el patrón de "higher-order function".
Las funciones como `translate()`, `rotate()` y `scale()` no
transforman un objeto directamente. En su lugar, retornan
*otra función* (un closure) que sabe cómo aplicar esa
transformación a un objeto `Solid`.

Esto permite componerlas fácilmente usando `toolz.compose`.
"""

from typing import Callable, Tuple
import numpy as np
from .vectors import Matrix4x4
from .csg import Solid

# Tipado para una función de transformación (toma un Solid, retorna un Solid)
TransformFn = Callable[[Solid], Solid]

# --- Generadores de Matrices (Privados) ---

def _rotation_matrix(axis: str, degrees: float) -> Matrix4x4:
    """Crea una matriz de rotación (Euler)"""
    rad = np.radians(degrees)
    cos, sin = np.cos(rad), np.sin(rad)

    if axis == 'x':
        data = (
            1, 0, 0, 0,
            0, cos, -sin, 0,
            0, sin, cos, 0,
            0, 0, 0, 1
        )
    elif axis == 'y':
        data = (
            cos, 0, sin, 0,
            0, 1, 0, 0,
            -sin, 0, cos, 0,
            0, 0, 0, 1
        )
    elif axis == 'z':
        data = (
            cos, -sin, 0, 0,
            sin, cos, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1
        )
    else:
        raise ValueError("El eje de rotación debe ser 'x', 'y', o 'z'")

    return Matrix4x4(data)

def _translation_matrix(x: float = 0, y: float = 0, z: float = 0) -> Matrix4x4:
    """Crea una matriz de traslación"""
    return Matrix4x4((
        1, 0, 0, x,
        0, 1, 0, y,
        0, 0, 1, z,
        0, 0, 0, 1
    ))

def _scale_matrix(sx: float = 1, sy: float = 1, sz: float = 1) -> Matrix4x4:
    """Crea una matriz de escala"""
    return Matrix4x4((
        sx, 0, 0, 0,
        0, sy, 0, 0,
        0, 0, sz, 0,
        0, 0, 0, 1
    ))

# --- NUEVAS MATRICES DE TRANSFORMACIÓN ---

def _reflection_matrix(axis: str) -> Matrix4x4:
    """Crea una matriz de reflexión (espejo) sobre un plano"""
    if axis == 'xy': # Refleja a través del eje Z
        return _scale_matrix(1, 1, -1)
    elif axis == 'xz': # Refleja a través del eje Y
        return _scale_matrix(1, -1, 1)
    elif axis == 'yz': # Refleja a través del eje X
        return _scale_matrix(-1, 1, 1)
    else:
        raise ValueError("El plano de reflexión debe ser 'xy', 'xz', o 'yz'")

def _shear_matrix(
    xy: float = 0, xz: float = 0,
    yx: float = 0, yz: float = 0,
    zx: float = 0, zy: float = 0
) -> Matrix4x4:
    """Crea una matriz de cizallamiento (shear)"""
    return Matrix4x4((
        1,  xy, xz, 0,
        yx, 1,  yz, 0,
        zx, zy, 1,  0,
        0,  0,  0,  1
    ))

def _rotation_from_quaternion(q: Tuple[float, float, float, float]) -> Matrix4x4:
    """Crea una matriz de rotación desde un quaternion (w, x, y, z)"""
    w, x, y, z = q

    # Normalizar el quaternion
    norm = (w*w + x*x + y*y + z*z)**0.5
    if norm == 0: return Matrix4x4.identity()
    w, x, y, z = w/norm, x/norm, y/norm, z/norm

    xx, yy, zz = x*x, y*y, z*z
    xy, xz, xw = x*y, x*z, x*w
    yz, yw, zw = y*z, y*w, z*w

    return Matrix4x4((
        1 - 2*(yy + zz), 2*(xy - zw),     2*(xz + yw),     0,
        2*(xy + zw),     1 - 2*(xx + zz), 2*(yz - xw),     0,
        2*(xz - yw),     2*(yz + xw),     1 - 2*(xx + yy), 0,
        0,               0,               0,               1
    ))

# --- Funciones de Transformación (Públicas de Alto Nivel) ---

def translate(x: float = 0, y: float = 0, z: float = 0) -> TransformFn:
    """Retorna una función que aplica una traslación a un Sólido."""
    matrix = _translation_matrix(x, y, z)
    def apply_transform(solid: Solid) -> Solid:
        return solid.transform(matrix)
    return apply_transform

def scale(sx: float = 1, sy: float = 1, sz: float = 1) -> TransformFn:
    """Retorna una función que aplica una escala a un Sólido."""
    matrix = _scale_matrix(sx, sy, sz)
    def apply_transform(solid: Solid) -> Solid:
        return solid.transform(matrix)
    return apply_transform

def scale_uniform(s: float) -> TransformFn:
    """Retorna una función que aplica una escala uniforme a un Sólido."""
    return scale(s, s, s)

def rotate(axis: str, degrees: float) -> TransformFn:
    """Retorna una función que aplica una rotación (Euler) a un Sólido."""
    matrix = _rotation_matrix(axis, degrees)
    def apply_transform(solid: Solid) -> Solid:
        return solid.transform(matrix)
    return apply_transform

# --- NUEVAS FUNCIONES DE TRANSFORMACIÓN ---

def rotate_by_quaternion(q: Tuple[float, float, float, float]) -> TransformFn:
    """
    Retorna una función que aplica una rotación (Quaternion) a un Sólido.
    q: Tupla en formato (w, x, y, z)
    """
    matrix = _rotation_from_quaternion(q)
    def apply_transform(solid: Solid) -> Solid:
        return solid.transform(matrix)
    return apply_transform

def reflect(plane: str) -> TransformFn:
    """
    Retorna una función que aplica una reflexión (espejo) a un Sólido.
    plane: El plano sobre el cual reflejar ('xy', 'xz', o 'yz')
    """
    matrix = _reflection_matrix(plane)
    def apply_transform(solid: Solid) -> Solid:
        return solid.transform(matrix)
    return apply_transform

def shear(
    xy: float = 0, xz: float = 0,
    yx: float = 0, yz: float = 0,
    zx: float = 0, zy: float = 0
) -> TransformFn:
    """
    Retorna una función que aplica un cizallamiento (shear) a un Sólido.
    xy: factor de shear de X con respecto a Y
    xz: factor de shear de X con respecto a Z
    ...etc.
    """
    matrix = _shear_matrix(xy, xz, yx, yz, zx, zy)
    def apply_transform(solid: Solid) -> Solid:
        return solid.transform(matrix)
    return apply_transform