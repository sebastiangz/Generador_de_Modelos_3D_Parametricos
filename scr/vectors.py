"""
src.vectors
Implementación de Álgebra Lineal Funcional.
Define las estructuras de datos inmutables Vector3 y Matrix4x4.
"""

from dataclasses import dataclass
from typing import Callable, Tuple
import numpy as np
import math

@dataclass(frozen=True)
class Vector3:
    """
    Representa un vector 3D inmutable.
    Utiliza @dataclass(frozen=True) para garantizar la inmutabilidad
    y la igualdad basada en valores.
    """
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

def __add__(self, other: 'Vector3') -> 'Vector3':
    """Suma de vectores"""
    return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

def __sub__(self, other: 'Vector3') -> 'Vector3':
    """Resta de vectores"""
    return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

def __mul__(self, scalar: float) -> 'Vector3':
    """Multiplicación por escalar"""
    return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

def __truediv__(self, scalar: float) -> 'Vector3':
    """División por escalar"""
    if scalar == 0:
        raise ValueError("No se puede dividir un vector por cero")
    return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)

def dot(self, other: 'Vector3') -> float:
    """Producto punto"""
    return self.x * other.x + self.y * other.y + self.z * other.z

def cross(self, other: 'Vector3') -> 'Vector3':
    """Producto cruz"""
    return Vector3(
        self.y * other.z - self.z * other.y,
        self.z * other.x - self.x * other.z,
        self.x * other.y - self.y * other.x
    )

def magnitude(self) -> float:
    """Magnitud (longitud) del vector"""
    return math.sqrt(self.dot(self))

def normalize(self) -> 'Vector3':
    """Vector unitario en la misma dirección"""
    mag = self.magnitude()
    if mag == 0:
        return Vector3(0, 0, 0) # Retorna vector cero si la magnitud es cero
    return self / mag

def map(self, fn: Callable[[float], float]) -> 'Vector3':
    """Aplica una función a cada componente del vector"""
    return Vector3(fn(self.x), fn(self.y), fn(self.z))


@dataclass(frozen=True)
class Matrix4x4:
    """
    Representa una matriz de transformación 4x4 inmutable (homogénea).
    Los datos se almacenan en un tuple de 16 elementos (row-major).
    """
    data: Tuple[float, ...]

    def __post_init__(self):
        """Valida que la matriz tenga 16 elementos después de la inicialización"""
        if len(self.data) != 16:
            raise ValueError("Matrix4x4 debe ser inicializada con 16 elementos.")

    def as_numpy(self) -> np.ndarray:
        """Convierte el tuple a un array numpy 4x4"""
        return np.array(self.data, dtype=float).reshape(4, 4)

    def multiply(self, other: 'Matrix4x4') -> 'Matrix4x4':
        """Multiplicación de matrices (self * other)"""
        a = self.as_numpy()
        b = other.as_numpy()
        result = np.matmul(a, b)
        return Matrix4x4(tuple(result.flatten()))

    def apply_to_vector(self, v: Vector3) -> Vector3:
        """Aplica la transformación de la matriz a un Vector3 (punto)"""
        m = self.as_numpy()
        # Vector homogéneo (x, y, z, 1) para transformaciones afines
        vec = np.array([v.x, v.y, v.z, 1.0])
        result = np.matmul(m, vec)
        
        # Normalización W (para proyecciones, aunque aquí W suele ser 1)
        if result[3] != 0 and result[3] != 1:
            return Vector3(result[0] / result[3], result[1] / result[3], result[2] / result[3])
        
        return Vector3(result[0], result[1], result[2])

    def inverse(self) -> 'Matrix4x4':
        """Calcula la matriz inversa. Crítico para CSG."""
        try:
            inv_matrix = np.linalg.inv(self.as_numpy())
            return Matrix4x4(tuple(inv_matrix.flatten()))
        except np.linalg.LinAlgError:
            raise ValueError("La matriz no es invertible")

    @staticmethod
    def identity() -> 'Matrix4x4':
        """Retorna una matriz identidad 4x4"""
        return Matrix4x4((
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1
        ))