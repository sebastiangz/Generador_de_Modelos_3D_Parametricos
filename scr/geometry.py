"""
src.geometry
Primitivas geométricas básicas.
"""

import math
from .vectors import Vector3
from .csg import Solid, Bounds

def sphere(radius: float) -> Solid:
    """Crea un Sólido esfera centrado en el origen"""
    if radius <= 0:
        raise ValueError("El radio debe ser positivo")

    def contains(point: Vector3) -> bool:
        # Un punto está dentro si su magnitud es <= al radio
        return point.magnitude() <= radius

    bounds: Bounds = (
        Vector3(-radius, -radius, -radius),
        Vector3(radius, radius, radius)
    )
    return Solid(contains, bounds)

def box(width: float, height: float, depth: float) -> Solid:
    """
    Crea un Sólido caja (cubo/paralelepípedo) centrado en el origen.
    Esto también sirve como un 'prisma rectangular'.
    """
    if any(d <= 0 for d in [width, height, depth]):
        raise ValueError("Las dimensiones deben ser positivas")

    w2, h2, d2 = width / 2.0, height / 2.0, depth / 2.0

    def contains(point: Vector3) -> bool:
        # Un punto está dentro si sus coordenadas absolutas
        # son menores o iguales a la mitad de las dimensiones.
        return (
            abs(point.x) <= w2 and
            abs(point.y) <= h2 and
            abs(point.z) <= d2
        )

    bounds: Bounds = (
        Vector3(-w2, -h2, -d2),
        Vector3(w2, h2, d2)
    )
    return Solid(contains, bounds)

def cylinder(radius: float, height: float) -> Solid:
    """
    Crea un Sólido cilindro centrado en el origen,
    alineado con el eje Z.
    """
    if radius <= 0 or height <= 0:
        raise ValueError("El radio y la altura deben ser positivos")

    h2 = height / 2.0

    def contains(point: Vector3) -> bool:
        # Comprueba si está dentro del radio en el plano XY
        in_radius = (point.x**2 + point.y**2)**0.5 <= radius
        # Comprueba si está dentro de la altura en el eje Z
        in_height = abs(point.z) <= h2
        return in_radius and in_height

    bounds: Bounds = (
        Vector3(-radius, -radius, -h2),
        Vector3(radius, radius, h2)
    )
    return Solid(contains, bounds)

# --- NUEVAS PRIMITIVAS ---

def cone(radius: float, height: float) -> Solid:
    """
    Crea un Sólido cono centrado en el origen, alineado con el eje Z.
    """
    if radius <= 0 or height <= 0:
        raise ValueError("El radio y la altura deben ser positivos")

    h2 = height / 2.0

    def contains(point: Vector3) -> bool:
        if not abs(point.z) <= h2:
            return False

        # Interpolar linealmente el radio basado en la altura
        # En z = -h2, factor = 1.0 * radius
        # En z = +h2, factor = 0.0 * radius
        interp_factor = (h2 - point.z) / height
        radius_at_z = radius * interp_factor

        # Comprobar si está dentro del radio en esa "rebanada"
        return (point.x**2 + point.y**2)**0.5 <= radius_at_z

    bounds: Bounds = (
        Vector3(-radius, -radius, -h2),
        Vector3(radius, radius, h2)
    )
    return Solid(contains, bounds)

def torus(major_radius: float, minor_radius: float) -> Solid:
    """
    Crea un Sólido toro (donut) centrado en el origen,
    acostado sobre el plano XY.
    """
    if minor_radius <= 0 or major_radius <= 0:
        raise ValueError("Los radios deben ser positivos")
    if minor_radius > major_radius:
        print("Advertencia: El radio menor es mayor al radio mayor, el toro se auto-intersectará.")

    R, r = major_radius, minor_radius
    r_squared = r**2

    def contains(point: Vector3) -> bool:
        # ( (x^2 + y^2)^0.5 - R )^2 + z^2 <= r^2
        xy_dist = (point.x**2 + point.y**2)**0.5
        term_1 = (xy_dist - R)**2
        term_2 = point.z**2
        return (term_1 + term_2) <= r_squared

    bounds: Bounds = (
        Vector3(-R - r, -R - r, -r),
        Vector3(R + r, R + r, r)
    )
    return Solid(contains, bounds)

def pyramid(width: float, depth: float, height: float) -> Solid:
    """
    Crea una pirámide de base rectangular centrada en el origen.
    """
    if any(d <= 0 for d in [width, depth, height]):
        raise ValueError("Las dimensiones deben ser positivas")

    w2, d2, h2 = width / 2.0, depth / 2.0, height / 2.0

    def contains(point: Vector3) -> bool:
        if not abs(point.z) <= h2:
            return False

        # Interpolar linealmente el tamaño de la base
        interp_factor = (h2 - point.z) / height
        width_at_z = w2 * interp_factor
        depth_at_z = d2 * interp_factor

        return (abs(point.x) <= width_at_z) and (abs(point.y) <= depth_at_z)

    bounds: Bounds = (
        Vector3(-w2, -d2, -h2),
        Vector3(w2, d2, h2)
    )
    return Solid(contains, bounds)