"""
src.surfaces
Define funciones para crear superficies paramétricas.

Una superficie paramétrica es una función que toma dos
parámetros `u` y `v` (generalmente en el rango [0, 1])
y retorna un `Vector3` en el espacio.
"""

from typing import Callable, Tuple
import numpy as np
from .vectors import Vector3

# Tipo para una superficie paramétrica: (float, float) -> Vector3
ParametricSurface = Callable[[float, float], Vector3]

# Tipo para una curva 2D (usada para revolución)
# (float) -> (radio, altura)
Curve2D = Callable[[float], Tuple[float, float]]

def surface_of_revolution(
    curve_2d: Curve2D,
    axis: str = 'z'
) -> ParametricSurface:
    """
    Crea una superficie de revolución rotando una curva 2D
    alrededor de un eje. (Cumple con "Superficies de revolución")

    Args:
        curve_2d: Una función que toma `u` (0 a 1) y retorna (radio, altura).
                  Ejemplo: `lambda u: (u, u*2)` crea un cono.
                  Ejemplo: `lambda u: (math.sin(u * math.pi), u * 5)`
        axis: Eje de rotación (actualmente solo 'z' está implementado).
    """
    if axis != 'z':
        raise NotImplementedError("La revolución solo está implementada para el eje 'z'")

    def surface(u: float, v: float) -> Vector3:
        """
        u: Parámetro a lo largo de la curva 2D (0 a 1)
        v: Parámetro de rotación (0 a 1, mapeado a 0-2*pi)
        """
        # Obtener (radio, altura) de la curva 2D
        radius, height_z = curve_2d(u)

        # Ángulo de rotación
        angle = v * 2 * np.pi

        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        z = height_z

        return Vector3(x, y, z)

    return surface