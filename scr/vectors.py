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