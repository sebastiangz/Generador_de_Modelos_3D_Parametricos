import math
from functools import reduce

# Alias de tipos inmutables
Vertice = tuple[float, float, float]
Triangulo = tuple[Vertice, Vertice, Vertice]
Malla = tuple[Triangulo, ...]
Matriz4x4 = tuple[
    tuple[float, float, float, float],
    tuple[float, float, float, float],
    tuple[float, float, float, float],
    tuple[float, float, float, float],
]

# --- Operaciones con Vectores 3D ---

def sumar_vectores(u: Vertice, v: Vertice) -> Vertice:
    return (u[0] + v[0], u[1] + v[1], u[2] + v[2])

def restar_vectores(u: Vertice, v: Vertice) -> Vertice:
    return (u[0] - v[0], u[1] - v[1], u[2] - v[2])

def escalar_vector(v: Vertice, s: float) -> Vertice:
    return (v[0] * s, v[1] * s, v[2] * s)

def producto_punto(u: Vertice, v: Vertice) -> float:
    return u[0] * v[0] + u[1] * v[1] + u[2] * v[2]

def producto_cruz(u: Vertice, v: Vertice) -> Vertice:
    return (
        u[1] * v[2] - u[2] * v[1],
        u[2] * v[0] - u[0] * v[2],
        u[0] * v[1] - u[1] * v[0],
    )

def norma(v: Vertice) -> float:
    return math.sqrt(producto_punto(v, v))

def normalizar_vector(v: Vertice) -> Vertice:
    n = norma(v)
    return (0.0, 0.0, 0.0) if n == 0.0 else escalar_vector(v, 1.0 / n)

def calcular_normal_triangulo(tri: Triangulo) -> Vertice:
    """Calcula el vector normal unitario de un triángulo (v1, v2, v3)."""
    v1, v2, v3 = tri
    arista1 = restar_vectores(v2, v1)
    arista2 = restar_vectores(v3, v1)
    return normalizar_vector(producto_cruz(arista1, arista2))

# --- Operaciones Matriciales 4x4 (Coordenadas Homogéneas) ---

def matriz_identidad() -> Matriz4x4:
    return (
        (1.0, 0.0, 0.0, 0.0),
        (0.0, 1.0, 0.0, 0.0),
        (0.0, 0.0, 1.0, 0.0),
        (0.0, 0.0, 0.0, 1.0),
    )

def multiplicar_matrices(a: Matriz4x4, b: Matriz4x4) -> Matriz4x4:
    """Multiplica dos matrices 4x4 de forma pura."""
    b_transpuesta = tuple(zip(*b))
    return tuple(
        tuple(sum(x * y for x, y in zip(fila_a, col_b)) for col_b in b_transpuesta)
        for fila_a in a
    )  # type: ignore

def aplicar_matriz_a_vertice(m: Matriz4x4, v: Vertice) -> Vertice:
    """Aplica una transformación 4x4 a un vértice 3D (w=1)."""
    vh = (v[0], v[1], v[2], 1.0)
    res = tuple(sum(fila[i] * vh[i] for i in range(4)) for fila in m)
    w = res[3] if res[3] != 0.0 else 1.0
    return (res[0] / w, res[1] / w, res[2] / w)

# --- Propiedades Espaciales de la Malla ---

def extraer_vertices(malla: Malla) -> tuple[Vertice, ...]:
    """Aplana una malla de triángulos en una secuencia de vértices."""
    return tuple(vertice for triangulo in malla for vertice in triangulo)

def calcular_bounding_box(malla: Malla) -> tuple[Vertice, Vertice]:
    """Devuelve ((min_x, min_y, min_z), (max_x, max_y, max_z))."""
    vertices = extraer_vertices(malla)
    if not vertices:
        return ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
    xs, ys, zs = zip(*vertices)
    return ((min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs)))

def calcular_dimensiones(malla: Malla) -> Vertice:
    """Devuelve (ancho_x, alto_y, largo_z) del Bounding Box."""
    v_min, v_max = calcular_bounding_box(malla)
    return restar_vectores(v_max, v_min)