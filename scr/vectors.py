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
