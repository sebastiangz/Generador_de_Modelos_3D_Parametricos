import math
from typing import Callable
from algebra_lineal import Malla, Triangulo, Vertice, escalar_vector, sumar_vectores

SuperficieParametrica = Callable[[float, float], Vertice]

# --- Curvas Paramétricas Puras ---

def curva_bezier_cubica(
    p0: Vertice, p1: Vertice, p2: Vertice, p3: Vertice
) -> Callable[[float], Vertice]:
    """Devuelve una función pura B(t) con t en [0, 1] para una curva de Bézier cúbica."""
    def evaluar(t: float) -> Vertice:
        u = 1.0 - t
        b0 = escalar_vector(p0, u ** 3)
        b1 = escalar_vector(p1, 3.0 * (u ** 2) * t)
        b2 = escalar_vector(p2, 3.0 * u * (t ** 2))
        b3 = escalar_vector(p3, t ** 3)
        return sumar_vectores(sumar_vectores(b0, b1), sumar_vectores(b2, b3))
    return evaluar

# --- Teselación (Discretización Pura a Malla de Triángulos) ---

def teselar_superficie(
    superficie: SuperficieParametrica, pasos_u: int = 24, pasos_v: int = 24
) -> Malla:
    """Convierte cualquier función paramétrica S(u, v) en una Malla inmutable de triángulos."""
    us = tuple(i / pasos_u for i in range(pasos_u + 1))
    vs = tuple(j / pasos_v for j in range(pasos_v + 1))

    # Evaluar rejilla de vértices (u, v)
    rejilla = tuple(
        tuple(superficie(u, v) for v in vs)
        for u in us
    )

    # Dividir cada celda cuadrangular en 2 triángulos
    def celda_a_triangulos(i: int, j: int) -> tuple[Triangulo, Triangulo]:
        p00 = rejilla[i][j]
        p10 = rejilla[i + 1][j]
        p01 = rejilla[i][j + 1]
        p11 = rejilla[i + 1][j + 1]
        return ((p00, p10, p11), (p00, p11, p01))

    pares_triangulos = tuple(
        celda_a_triangulos(i, j)
        for i in range(pasos_u)
        for j in range(pasos_v)
    )
    return tuple(tri for par in pares_triangulos for tri in par)

# --- Modelos Paramétricos Característicos de Armas ---

def generar_canon_parametrico(radio: float = 0.08, longitud: float = 1.6) -> Malla:
    """Genera la malla 3D de un cañón cilíndrico alineado en el eje Z."""
    def s_canon(u: float, v: float) -> Vertice:
        theta = 2.0 * math.pi * u
        x = radio * math.cos(theta)
        y = radio * math.sin(theta)
        z = (v - 0.5) * longitud
        return (x, y, z)

    return teselar_superficie(s_canon, pasos_u=24, pasos_v=12)

def generar_empunadura_parametrica(
    ancho: float = 0.14, grosor: float = 0.09, alto: float = 0.65
) -> Malla:
    """Genera una empuñadura ergonómica extruyendo una sección elíptica sobre una curva de Bézier."""
    espina = curva_bezier_cubica(
        (0.0, 0.0, -0.3),
        (0.0, -alto * 0.35, -0.38),
        (0.0, -alto * 0.70, -0.46),
        (0.0, -alto, -0.52),
    )

    def s_empunadura(u: float, v: float) -> Vertice:
        theta = 2.0 * math.pi * u
        cx, cy, cz = espina(v)
        # Ligero estrechamiento en la parte media del agarre
        factor_agarre = 1.0 - 0.15 * math.sin(math.pi * v)
        x = cx + (grosor * factor_agarre) * math.cos(theta)
        y = cy
        z = cz + (ancho * factor_agarre) * math.sin(theta)
        return (x, y, z)

    return teselar_superficie(s_empunadura, pasos_u=20, pasos_v=16)

def generar_hoja_punzocortante(
    largo: float = 1.6, ancho_base: float = 0.22, grosor_lomo: float = 0.04
) -> Malla:
    """Genera la hoja de un arma punzocortante con filo doble y punta convergente."""
    def s_hoja(u: float, v: float) -> Vertice:
        # v in [0, 1] recorre desde la base hasta la punta
        perfil_punta = math.sqrt(max(0.0, 1.0 - (v ** 2.2)))
        ancho_actual = ancho_base * perfil_punta
        grosor_actual = grosor_lomo * perfil_punta

        # u in [0, 1] recorre el perímetro romboidal de la sección transversal (filo-lomo-filo)
        angulo = 2.0 * math.pi * u
        x = (grosor_actual / 2.0) * math.sin(angulo)
        y = (ancho_actual / 2.0) * math.cos(angulo)
        z = (v - 0.5) * largo
        return (x, y, z)

    return teselar_superficie(s_hoja, pasos_u=16, pasos_v=20)