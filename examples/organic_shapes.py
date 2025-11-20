"""
gears.py

Generador paramétrico de un engranaje simple.
Demuestra:
- Uso de primitivas (cylinder, box).
- Composición de transformaciones (rotate, translate).
- Operaciones CSG (difference, union).
"""

from src.geometry import cylinder, box
from src.transforms import translate, rotate
from src.csg import difference, union
from toolz import pipe, compose
from src.csg import Solid
import math

def create_gear(
    radius: float, 
    height: float, 
    teeth: int, 
    tooth_width: float, 
    tooth_depth: float
) -> 'Solid':
    """
    Crea un engranaje usando diferencia booleana.
    """
    
    # 1. Cilindro base del engranaje
    base_solid = cylinder(radius=radius, height=height)
    
    # 2. El 'agujero' de corte para generar los dientes
    # Usamos una caja lo suficientemente larga para cortar el radio + profundidad.
    cutter_width = (radius + tooth_depth) * 2.0
    cutter_height = height * 1.5 # Más alto que el engranaje para asegurar el corte
    
    # El diente se corta en el borde, así que el centro del cutter debe estar fuera del radio.
    # Posición inicial: centro del cutter en X = radio + depth/2
    initial_x_position = radius + (tooth_depth / 2.0)
    
    # El cutter es una caja del tamaño del espacio entre los dientes.
    cutter_solid = box(width=tooth_width, height=cutter_height, depth=cutter_width)
    
    # La operación para trasladar el cutter a su posición inicial
    initial_translation = translate(x=initial_x_position)
    
    # Lista para almacenar todos los 'cortadores' transformados
    all_cutters = []
    
    angle_step = 360.0 / teeth
    
    for i in range(teeth):
        angle = i * angle_step
        
        # Secuencia de transformación:
        # 1. Trasladar el cutter a la posición inicial (fuera del radio)
        # 2. Rotarlo por el ángulo del diente actual
        
        # compose(rotate, translate)
        transform_fn = compose(
            rotate(axis='z', degrees=angle),
            initial_translation
        )
        
        # Aplicar la composición al cutter y añadirlo a la lista
        transformed_cutter = transform_fn(cutter_solid)
        all_cutters.append(transformed_cutter)
        
    # 3. La operación final es la Diferencia (base - union de todos los cortes)
    
    # Reducir la lista de cortadores a un solo sólido grande (Union)
    # Se usa pipe para una forma funcional de encadenar la reducción
    cutters_union = pipe(
        all_cutters[1:], 
        lambda solids: union(all_cutters[0], solids[0]),
        lambda result, next_solid: union(result, next_solid) # Simplificación: usar union_many si estuviera implementado
    )
    
    # Retornar el engranaje final
    return difference(base_solid, cutters_union)

# --- USO ---
if __name__ == '__main__':
    from src.export import export_stl 
    
    gear_model = create_gear(
        radius=10.0, 
        height=5.0, 
        teeth=16, 
        tooth_width=1.5,
        tooth_depth=2.0
    )

    print("Generando engranaje...")
    # La función de exportación se encargará del meshing (Marching Cubes)
    # Asegúrate de que export_stl esté configurado para usar src.mesh
    export_stl(gear_model, 'models/gear_final.stl', resolution=100)
    print("Engranaje exportado a models/gear_final.stl")