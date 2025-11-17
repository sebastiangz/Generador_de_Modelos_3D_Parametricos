"""
src.export
Funciones para exportar los Sólidos a formatos de archivo estándar.

Estas funciones unen el mundo funcional (CSG) con el mundo
poligonal (STL, OBJ). Toman un objeto `Solid` y utilizan
el módulo `mesh` para convertirlo en una malla antes de
guardarlo en un archivo.
"""

import trimesh
import numpy as np
from typing import Tuple, Optional, List

from .csg import Solid
from .mesh import mesh_from_solid, mesh_from_surface
from .surfaces import ParametricSurface
from .vectors import Vector3 # Necesario para la función PLY

def export_stl(
    solid: Solid,
    filename: str,
    resolution: int = 75,
    ascii: bool = False
):
    """
    Exporta un Sólido CSG a un archivo STL.
    Cumple con: STL (ASCII y Binary)

    Args:
        solid: El Sólido a exportar.
        filename: Nombre del archivo (ej. 'modelo.stl').
        resolution: Resolución del marching cubes. Más alto = más detalle.
        ascii: Si es True, exporta en STL ASCII.
               Si es False (default), exporta en STL Binario (más rápido y pequeño).
    """
    if not filename.lower().endswith('.stl'):
        filename += '.stl'

    print(f"Iniciando mallado (meshing) para {filename} (resolución={resolution})...")
    try:
        mesh_obj = mesh_from_solid(solid, resolution=resolution)

        if not mesh_obj.is_empty:
            # Determinar el 'encoding' para trimesh
            # None (default) usa binario, 'ascii' usa ASCII.
            encoding = 'ascii' if ascii else None
            mesh_obj.export(filename, file_type='stl', encoding=encoding)

            format_type = "ASCII" if ascii else "Binario"
            print(f"Archivo guardado exitosamente: {filename} ({format_type})")
        else:
            print("Advertencia: El mesh resultante estaba vacío. No se guardó el archivo.")

    except Exception as e:
        print(f"Error durante la exportación a STL: {e}")

def export_obj(
    solid: Solid,
    filename: str,
    resolution: int = 75,
    color: Optional[Tuple[int, int, int]] = None
):
    """
    Exporta un Sólido CSG a un archivo OBJ.
    Cumple con: OBJ con materiales (básico)

    Args:
        solid: El Sólido a exportar.
        filename: Nombre del archivo (ej. 'modelo.obj').
        resolution: Resolución del marching cubes.
        color: Un color difuso (R, G, B) de 0-255.
               Si se provee, se generará un archivo .mtl y se enlazará.
    """
    if not filename.lower().endswith('.obj'):
        filename += '.obj'

    print(f"Iniciando mallado (meshing) para {filename} (resolución={resolution})...")
    try:
        mesh_obj = mesh_from_solid(solid, resolution=resolution)

        if not mesh_obj.is_empty:
            # Si se proporciona un color, asignarlo al material del mesh
            if color:
                print(f"Asignando material (color={color}) y generando .mtl...")
                # Añadir canal alfa (opacidad) al color, trimesh espera RGBA
                color_rgba = (*color, 255)
                # Asignar el color. trimesh creará el .mtl al exportar.
                mesh_obj.visual = trimesh.visual.ColorVisuals(face_colors=color_rgba)

            mesh_obj.export(filename, file_type='obj')
            print(f"Archivo guardado exitosamente: {filename}")
        else:
            print("Advertencia: El mesh resultante estaba vacío. No se guardó el archivo.")

    except Exception as e:
        print(f"Error durante la exportación a OBJ: {e}")

def export_surface_stl(
    surface_fn: ParametricSurface,
    filename: str,
    u_range: tuple = (0, 1),
    v_range: tuple = (0, 1),
    u_steps: int = 50,
    v_steps: int = 50,
    ascii: bool = False
):
    """
    Exporta una Superficie Paramétrica directamente a STL.
    Cumple con: STL (ASCII y Binary) para superficies.
    """
    if not filename.lower().endswith('.stl'):
        filename += '.stl'

    print(f"Generando mesh para superficie {filename} (pasos={u_steps}x{v_steps})...")
    try:
        mesh_obj = mesh_from_surface(surface_fn, u_range, v_range, u_steps, v_steps)

        encoding = 'ascii' if ascii else None
        mesh_obj.export(filename, file_type='stl', encoding=encoding)

        format_type = "ASCII" if ascii else "Binario"
        print(f"Archivo de superficie guardado: {filename} ({format_type})")
    except Exception as e:
        print(f"Error durante la exportación de superficie: {e}")

def export_ply_point_cloud(
    points: List[Vector3],
    filename: str,
    colors: Optional[List[Tuple[int, int, int]]] = None,
    ascii: bool = False
):
    """
    Exporta una lista de puntos (nube de puntos) a un archivo PLY.
    Cumple con: PLY para point clouds

    Args:
        points: Una lista de objetos Vector3.
        filename: Nombre del archivo (ej. 'nube.ply').
        colors: (Opcional) Una lista de tuplas (R, G, B) [0-255],
                una por cada punto.
        ascii: Si es True, exporta en PLY ASCII.
               Si es False (default), exporta en PLY Binario.
    """
    if not filename.lower().endswith('.ply'):
        filename += '.ply'

    print(f"Preparando nube de {len(points)} puntos para {filename}...")

    try:
        # Convertir la lista de Vector3 a un array numpy (Nx3)
        points_np = np.array([[p.x, p.y, p.z] for p in points], dtype=float)

        colors_np = None
        if colors:
            if len(colors) != len(points):
                print(f"Advertencia: La lista de colores ({len(colors)}) no coincide "
                      f"con la lista de puntos ({len(points)}). Se ignorarán los colores.")
            else:
                # Trimesh espera RGBA
                colors_np = [(*c, 255) for c in colors]
                print("Se incluirán colores en el archivo PLY.")

        # Crear un objeto PointCloud de trimesh
        pc_obj = trimesh.PointCloud(vertices=points_np, colors=colors_np)

        # Determinar el encoding correctamente
        encoding = 'ascii' if ascii else None

        # Llamar a la función de exportar
        pc_obj.export(filename, file_type='ply', encoding=encoding)

        format_type = "ASCII" if ascii else "Binario"
        print(f"Nube de puntos guardada exitosamente: {filename} ({format_type})")

    except Exception as e:
        print(f"Error durante la exportación a PLY: {e}")