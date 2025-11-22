import os
import sys
from functools import reduce

# Ajustar path para importar src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.vectors import Vector3
from src.geometry import box, cylinder, pyramid
from src.transforms import translate, rotate, scale
from src.csg import union, difference, Solid
from src.export import export_stl

# --- 1. COMPONENTES MODULARES (Las piezas de Lego) ---

def create_floor_segment(width: float, height: float) -> Solid:
    """
    Crea un piso individual.
    Consiste en una losa (box) y 4 columnas en las esquinas.
    """
    # 1. La Losa (Suelo)
    slab = box(width, height, width)
    
    # 2. Columnas (Cilindros en las esquinas)
    col_radius = width * 0.1
    col_height = height * 3 # Las columnas son más altas para conectar pisos
    col_offset = width / 2.0 - col_radius
    
    # Creamos una columna base
    column = cylinder(col_radius, col_height)
    
    # Posicionamos las 4 columnas
    c1 = translate(x=col_offset, y=col_offset)(column)
    c2 = translate(x=-col_offset, y=col_offset)(column)
    c3 = translate(x=col_offset, y=-col_offset)(column)
    c4 = translate(x=-col_offset, y=-col_offset)(column)
    
    # Unimos todo en un solo bloque "Piso"
    # Usamos reduce para unir una lista de objetos secuencialmente
    parts = [slab, c1, c2, c3, c4]
    floor_structure = reduce(union, parts)
    
    return floor_structure

def create_roof_antenna(width: float) -> Solid:
    """Crea una antena piramidal para el techo"""
    base = box(width, 2, width)
    spire = pyramid(width * 0.8, width * 0.8, height=15)
    # Subir la espira para que esté sobre la base
    spire_moved = translate(z=8)(spire)
    return union(base, spire_moved)

# --- 2. GENERADOR PROCEDIMENTAL (El Arquitecto) ---

def build_twisted_tower(
    floors: int = 20, 
    floor_width: float = 10.0, 
    floor_height: float = 2.0,
    twist_angle: float = 5.0
) -> Solid:
    """
    Genera una torre completa apilando pisos y rotándolos progresivamente.
    """
    generated_floors = []
    
    # Creamos el modelo base de un piso
    base_floor = create_floor_segment(floor_width, floor_height)
    
    for i in range(floors):
        # Calcular transformaciones para este piso específico
        # 1. Subir (z)
        elevation = i * floor_height * 1.2 # 1.2 para dejar espacio visual
        # 2. Girar (z)
        rotation = i * twist_angle
        
        # Aplicar transformaciones: Primero rotar, luego subir
        # (El orden importa: si subes y luego rotas, rotarías alrededor del origen mundial)
        transform_fn = translate(z=elevation)
        rotate_fn = rotate(axis='z', degrees=rotation)
        
        # Aplicar al piso base
        # Nota: En nuestra lógica funcional, aplicamos rotation primero al objeto, 
        # y al resultado lo trasladamos.
        current_floor = transform_fn(rotate_fn(base_floor))
        
        generated_floors.append(current_floor)
    
    # Unir todos los pisos en un solo edificio
    tower_body = reduce(union, generated_floors)
    
    # Agregar el techo
    total_height = floors * floor_height * 1.2
    final_rotation = floors * twist_angle
    
    roof = create_roof_antenna(floor_width)
    # Mover el techo al tope y rotarlo igual que el último piso
    roof_transformed = translate(z=total_height)(
        rotate(axis='z', degrees=final_rotation)(roof)
    )
    
    return union(tower_body, roof_transformed)

# --- 3. EJECUCIÓN ---

if __name__ == '__main__':
    print("🏗️ Iniciando Arquitecto Paramétrico...")
    
    # Parámetros de diseño
    N_PISOS = 25
    ANCHO = 12.0
    GIRO = 10.0 # Grados por piso
    
    print(f"Diseñando torre de {N_PISOS} pisos con giro de {GIRO} grados...")
    
    # Generar la torre
    skyscraper = build_twisted_tower(
        floors=N_PISOS, 
        floor_width=ANCHO, 
        twist_angle=GIRO
    )
    
    # Definir ruta de salida
    output_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'twisted_tower.stl')
    
    print("Generando geometría (esto puede tardar un poco por la cantidad de uniones)...")
    # Resolution 60 es suficiente para bloques rectos
    export_stl(skyscraper, output_path, resolution=60)
    
    print(f"✅ Edificio construido en: {output_path}")