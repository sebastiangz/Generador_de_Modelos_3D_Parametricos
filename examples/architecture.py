"""
architecture.py

Generación de un modelo arquitectónico (columna hueca con base).
Demuestra:
- Encadenamiento de operaciones.
- Creación de un modelo hueco (Diferencia).
- Uso de composiciones complejas (pipe).
"""

from src.geometry import box, cylinder
from src.transforms import translate, scale, scale_uniform, rotate
from src.csg import difference, union
from toolz import pipe
from src.csg import Solid
import math

# --- Funciones Composables ---

def make_pedestal(size: float, height: float) -> 'Solid':
    """Crea la base de la columna (un prisma ancho y bajo)."""
    return box(size, height, size)

def make_shaft_hollow(radius: float, height: float, thickness: float) -> 'Solid':
    """Crea el fuste (cuerpo) de la columna como un tubo."""
    # Cilindro exterior
    outer = cylinder(radius=radius, height=height)
    # Cilindro interior (el hueco)
    inner_radius = radius - thickness
    if inner_radius <= 0:
        raise ValueError("El grosor es demasiado grande para el radio.")
        
    hole = cylinder(radius=inner_radius, height=height * 1.5) # Asegurar corte total
    
    # El hueco se crea usando diferencia
    return difference(outer, hole)

# --- Construcción del Modelo Final ---

def create_column(pedestal_size=20, pedestal_h=5, shaft_r=8, shaft_h=80, shaft_t=1) -> 'Solid':
    
    # 1. Base (Pedestal)
    pedestal = make_pedestal(pedestal_size, pedestal_h)
    
    # Ajustar el pedestal para que su base esté en Z=0
    # Está centrado, así que necesita ser trasladado por pedestal_h/2
    translate_pedestal_up = translate(z=pedestal_h / 2.0)
    final_pedestal = translate_pedestal_up(pedestal)
    
    # 2. Fuste (Shaft)
    shaft = make_shaft_hollow(shaft_r, shaft_h, shaft_t)
    
    # Trasladar el fuste para que descanse sobre el pedestal.
    # El centro del pedestal está en pedestal_h/2. El centro del shaft debe estar 
    # en pedestal_h + shaft_h/2.
    z_center_shaft = pedestal_h + (shaft_h / 2.0)
    
    translate_shaft_up = translate(z=z_center_shaft)
    final_shaft = translate_shaft_up(shaft)
    
    # 3. Capital (Tope de la Columna - un cubo simple por simplicidad)
    capital_size = pedestal_size * 0.8
    capital_h = pedestal_h * 1.5
    capital = box(capital_size, capital_size, capital_h)
    
    # Trasladar el tope sobre el fuste
    z_center_capital = pedestal_h + shaft_h + (capital_h / 2.0)
    translate_capital_up = translate(z=z_center_capital)
    final_capital = translate_capital_up(capital)
    
    # 4. Unión final de las partes (Composición Funcional)
    # pipe(input, fn1, fn2, ...)
    final_column = pipe(
        final_pedestal,
        lambda s: union(s, final_shaft),
        lambda s: union(s, final_capital)
    )
    
    return final_column

# --- USO ---
if __name__ == '__main__':
    from src.export import export_stl 
    
    column_model = create_column()
    
    print("Generando columna arquitectónica...")
    export_stl(column_model, 'models/arch_column.stl', resolution=100)
    print("Columna exportada a models/arch_column.stl")