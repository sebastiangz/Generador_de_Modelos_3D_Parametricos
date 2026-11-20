import struct
from pathlib import Path
from algebra_lineal import Malla, Triangulo, Vertice, calcular_normal_triangulo

def _es_stl_binario(datos: bytes) -> bool:
    """Determina si el archivo STL es binario verificando su tamaño exacto."""
    if len(datos) < 84:
        return False
    num_triangulos = struct.unpack("<I", datos[80:84])[0]
    tamano_esperado = 84 + (num_triangulos * 50)
    return len(datos) == tamano_esperado

def _parsear_stl_binario(datos: bytes) -> Malla:
    """Extrae triángulos de un buffer binario STL usando unpacking puro."""
    num_triangulos = struct.unpack("<I", datos[80:84])[0]
    
    def leer_triangulo(indice: int) -> Triangulo:
        offset = 84 + (indice * 50)
        coords = struct.unpack("<9f", datos[offset + 12 : offset + 48])
        return (
            (coords[0], coords[1], coords[2]),
            (coords[3], coords[4], coords[5]),
            (coords[6], coords[7], coords[8]),
        )

    return tuple(map(leer_triangulo, range(num_triangulos)))

def _parsear_stl_ascii(texto: str) -> Malla:
    """Extrae triángulos de un texto STL ASCII filtrando líneas de vértices."""
    lineas_vertex = tuple(
        linea.strip().split()
        for linea in texto.splitlines()
        if linea.strip().startswith("vertex")
    )
    vertices = tuple(
        (float(partes[1]), float(partes[2]), float(partes[3]))
        for partes in lineas_vertex
    )
    return tuple(
        (vertices[i], vertices[i + 1], vertices[i + 2])
        for i in range(0, len(vertices) - 2, 3)
    )

def cargar_stl(ruta: Path) -> Malla:
    """Carga un archivo STL (binario o ASCII) y devuelve una Malla inmutable."""
    datos = ruta.read_bytes()
    if _es_stl_binario(datos):
        return _parsear_stl_binario(datos)
    return _parsear_stl_ascii(datos.decode("utf-8", errors="ignore"))

def _formatear_triangulo_stl(tri: Triangulo) -> str:
    nx, ny, nz = calcular_normal_triangulo(tri)
    v1, v2, v3 = tri
    return (
        f"  facet normal {nx:.6f} {ny:.6f} {nz:.6f}\n"
        f"    outer loop\n"
        f"      vertex {v1[0]:.6f} {v1[1]:.6f} {v1[2]:.6f}\n"
        f"      vertex {v2[0]:.6f} {v2[1]:.6f} {v2[2]:.6f}\n"
        f"      vertex {v3[0]:.6f} {v3[1]:.6f} {v3[2]:.6f}\n"
        f"    endloop\n"
        f"  endfacet"
    )

def exportar_stl(malla: Malla, ruta_salida: Path, nombre_solido: str = "modelo_3d") -> None:
    """Serializa la malla a formato STL ASCII y la guarda en disco."""
    cuerpo = "\n".join(map(_formatear_triangulo_stl, malla))
    contenido = f"solid {nombre_solido}\n{cuerpo}\nendsolid {nombre_solido}\n"
    ruta_salida.write_text(contenido, encoding="utf-8")

def exportar_obj(malla: Malla, ruta_salida: Path, nombre_objeto: str = "modelo_3d") -> None:
    """Serializa la malla a formato Wavefront OBJ estándar y la guarda en disco."""
    lineas_vertices = tuple(
        f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}"
        for tri in malla
        for v in tri
    )
    lineas_caras = tuple(
        f"f {i * 3 + 1} {i * 3 + 2} {i * 3 + 3}"
        for i in range(len(malla))
    )
    contenido = (
        f"# Exportado por Detector de Armas 3D\n"
        f"o {nombre_objeto}\n"
        + "\n".join(lineas_vertices)
        + "\n"
        + "\n".join(lineas_caras)
        + "\n"
    )
    ruta_salida.write_text(contenido, encoding="utf-8")