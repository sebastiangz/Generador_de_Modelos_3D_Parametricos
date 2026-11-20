from pathlib import Path
from functools import partial
from io_meshes import cargar_stl, exportar_stl, exportar_obj
from transformaciones import normalizar_malla
from clasificador import evaluar_similitud_csg

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
    
    procesar_archivo = lambda ruta: (
        ruta.stem, 
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
    referencias = cargar_referencias(DIR_ASSETS)
    
    ruta_entrada = obtener_archivo_entrada(DIR_INPUT)
    malla_desconocida = normalizar_malla(cargar_stl(ruta_entrada))
    
    resultados = tuple(
        map(
            lambda ref: (ref[0], evaluar_similitud_csg(malla_desconocida, ref[1])),
            referencias
        )
    )
    
    mejor_categoria, similitud = max(resultados, key=lambda item: item[1])
    
    etiqueta = mejor_categoria if similitud >= 0.65 else "objeto_cotidiano_no_identificado"
    
    DIR_OUTPUT.mkdir(exist_ok=True)
    nombre_salida = f"{ruta_entrada.stem}_clasificado_{etiqueta}_{int(similitud * 100)}pct"
    
    exportar_stl(malla_desconocida, DIR_OUTPUT / f"{nombre_salida}.stl")
    exportar_obj(malla_desconocida, DIR_OUTPUT / f"{nombre_salida}.obj")
    
    print(f"Archivo analizado: {ruta_entrada.name}")
    for cat, score in resultados:
        print(f"  - Similitud con {cat}: {score * 100:.2f}%")
    print(f"Resultado final: {etiqueta.upper()}")


if __name__ == "__main__":
    ejecutar_pipeline()