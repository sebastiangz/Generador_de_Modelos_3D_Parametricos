from pathlib import Path
from functools import partial
# Asumiendo que tus funciones puras ya existen en estos módulos:
from io_meshes import cargar_stl, exportar_stl, exportar_obj
from transformaciones import normalizar_malla
from clasificador import evaluar_similitud_csg

# Definición de rutas base inmutables respecto a src/
BASE_DIR = Path(__file__).resolve().parent.parent
DIR_ASSETS = BASE_DIR / "3D_assets"
DIR_INPUT = BASE_DIR / "input_analizar"
DIR_OUTPUT = BASE_DIR / "output_clasificados"


def cargar_referencias(directorio: Path) -> tuple[tuple[str, tuple], ...]:
    """
    Lee todos los .stl de 3D_assets, los normaliza y devuelve una tupla inmutable
    de pares: ((nombre_categoria, malla_normalizada), ...)
    """
    archivos_stl = tuple(sorted(directorio.glob("*.stl")))
    
    # Pipeline puro: Path -> (nombre, malla_cruda) -> (nombre, malla_normalizada)
    procesar_archivo = lambda ruta: (
        ruta.stem,  # Ej. "armas_corta", "Misil", "punzocortantes"
        normalizar_malla(cargar_stl(ruta))
    )
    
    return tuple(map(procesar_archivo, archivos_stl))


def obtener_archivo_entrada(directorio: Path) -> Path:
    """Obtiene el primer archivo .stl encontrado en input_analizar/."""
    archivos = tuple(directorio.glob("*.stl"))
    if not archivos:
        raise FileNotFoundError(f"No se encontró ningún archivo .stl en {directorio}")
    return archivos[0]
def ejecutar_pipeline() -> None:
    # 1. Cargar y normalizar plantillas de 3D_assets/
    referencias = cargar_referencias(DIR_ASSETS)
    
    # 2. Cargar y normalizar el objeto desconocido de input_analizar/
    ruta_entrada = obtener_archivo_entrada(DIR_INPUT)
    malla_desconocida = normalizar_malla(cargar_stl(ruta_entrada))
    
    # 3. Evaluar coincidencia CSG contra cada referencia de forma pura
    # Devuelve tuplas: ((categoria, puntaje_iou), ...)
    resultados = tuple(
        map(
            lambda ref: (ref[0], evaluar_similitud_csg(malla_desconocida, ref[1])),
            referencias
        )
    )
    
    # 4. Seleccionar la mejor coincidencia (mayor porcentaje de intersección)
    mejor_categoria, similitud = max(resultados, key=lambda item: item[1])
    
    # Definir etiqueta final según umbral (por ejemplo, 65% de coincidencia)
    etiqueta = mejor_categoria if similitud >= 0.65 else "objeto_cotidiano_no_identificado"
    
    # 5. Exportar malla normalizada y etiquetada en STL y OBJ
    DIR_OUTPUT.mkdir(exist_ok=True)
    nombre_salida = f"{ruta_entrada.stem}_clasificado_{etiqueta}_{int(similitud * 100)}pct"
    
    exportar_stl(malla_desconocida, DIR_OUTPUT / f"{nombre_salida}.stl")
    exportar_obj(malla_desconocida, DIR_OUTPUT / f"{nombre_salida}.obj")
    
    # Reporte en consola
    print(f"Archivo analizado: {ruta_entrada.name}")
    for cat, score in resultados:
        print(f"  - Similitud con {cat}: {score * 100:.2f}%")
    print(f"Resultado final: {etiqueta.upper()}")


if __name__ == "__main__":
    ejecutar_pipeline()