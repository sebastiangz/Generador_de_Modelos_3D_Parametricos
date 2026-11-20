import math
from algebra_lineal import Malla, calcular_dimensiones
from csg import calcular_iou_csg, malla_a_sdf, union
from geometria_parametrica import (
    generar_canon_parametrico,
    generar_empunadura_parametrica,
    generar_hoja_punzocortante,
)
from transformaciones import normalizar_malla

def extraer_proporciones_espaciales(malla: Malla) -> tuple[float, float, float]:
    """
    Calcula las proporciones normalizadas (ancho_rel, alto_rel, largo_rel)
    ordenadas respecto a la dimensión máxima de la malla.
    """
    dx, dy, dz = calcular_dimensiones(malla)
    max_d = max(dx, dy, dz)
    if max_d == 0.0:
        return (0.0, 0.0, 0.0)
    return (dx / max_d, dy / max_d, dz / max_d)

def similitud_proporciones(malla_a: Malla, malla_b: Malla) -> float:
    """
    Evalúa qué tan parecidas son las proporciones espaciales (Bounding Box)
    entre dos modelos 3D en un rango de [0.0, 1.0].
    """
    pa = extraer_proporciones_espaciales(malla_a)
    pb = extraer_proporciones_espaciales(malla_b)
    distancia_euclidiana = math.sqrt(
        sum((a - b) ** 2 for a, b in zip(pa, pb))
    )
    return max(0.0, 1.0 - (distancia_euclidiana / math.sqrt(3.0)))

def construir_plantilla_parametrica(tipo_arma: str) -> Malla:
    """
    Combina mallas generadas por funciones paramétricas para crear plantillas
    ideales de referencia (cañón + empuñadura o hoja punzocortante).
    """
    if tipo_arma == "armas_corta":
        canon = generar_canon_parametrico(radio=0.10, longitud=1.0)
        empunadura = generar_empunadura_parametrica(ancho=0.16, grosor=0.10, alto=0.65)
        return normalizar_malla(canon + empunadura)
    if tipo_arma == "armas_largas":
        canon = generar_canon_parametrico(radio=0.06, longitud=1.8)
        empunadura = generar_empunadura_parametrica(ancho=0.14, grosor=0.09, alto=0.55)
        return normalizar_malla(canon + empunadura)
    if tipo_arma == "punzocortantes":
        hoja = generar_hoja_punzocortante(largo=1.6, ancho_base=0.22, grosor_lomo=0.04)
        return normalizar_malla(hoja)
    return ()

def evaluar_similitud_csg(malla_desconocida: Malla, malla_referencia: Malla) -> float:
    """
    Calcula el puntaje total de coincidencia [0.0, 1.0] combinando:
    - 65% Coincidencia volumétrica CSG (Intersection / Union de sólidos SDF)
    - 35% Coincidencia de proporciones espaciales (Álgebra lineal)
    """
    sdf_desconocido = malla_a_sdf(malla_desconocida)
    sdf_referencia = malla_a_sdf(malla_referencia)

    score_csg = calcular_iou_csg(sdf_desconocido, sdf_referencia)
    score_prop = similitud_proporciones(malla_desconocida, malla_referencia)

    return (0.65 * score_csg) + (0.35 * score_prop)