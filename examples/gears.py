import os
import sys
import numpy as np
from PIL import Image
from toolz import compose

# Ajustar path para importar src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.geometry import cylinder, box
from src.transforms import translate, rotate, scale
from src.csg import difference, union, Solid
from src.export import export_stl

# --- 1. FUNCIONES PARA PROCESAR IMAGEN (LO QUE FALTABA) ---

def load_image_as_mask(image_path: str, threshold: int = 128) -> np.ndarray:
    """Carga la imagen y detecta píxeles negros."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"¡No se encuentra la imagen: {image_path}!")
    
    img = Image.open(image_path).convert('L') # Escala de grises
    data = np.array(img)
    # True donde es oscuro (negro), False donde es claro (blanco)
    return data < threshold

def image_solid(mask: np.ndarray, width: float, height: float, thickness: float) -> Solid:
    """Convierte la máscara de la imagen en un objeto 3D."""
    img_h, img_w = mask.shape
    w2, h2, d2 = width / 2.0, height / 2.0, thickness / 2.0

    def contains(p):
        # Verificar límites físicos
        if not (abs(p.x) <= w2 and abs(p.y) <= h2 and abs(p.z) <= d2):
            return False
        
        # Mapear 3D -> 2D Píxel
        u = (p.x + w2) / width
        v = (p.y + h2) / height
        px = int(u * (img_w - 1))
        py = int((1 - v) * (img_h - 1)) # Invertir Y
        
        # Verificar límites de array por seguridad
        if 0 <= px < img_w and 0 <= py < img_h:
            return mask[py, px]
        return False

    bounds = (
        type('Vector3', (), {'x': -w2, 'y': -h2, 'z': -d2}), # Hack rápido para bounds
        type('Vector3', (), {'x': w2, 'y': h2, 'z': d2})
    )
    # Nota: Usamos la clase Solid real importada, los bounds aquí son referenciales
    # para que coincida con tu implementación de src.csg
    from src.vectors import Vector3
    real_bounds = (Vector3(-w2, -h2, -d2), Vector3(w2, h2, d2))
    return Solid(contains, real_bounds)

# --- 2. GENERADOR DE ENGRANAJE BASE ---

def create_simple_gear(radius=15.0, thickness=5.0, teeth=12) -> Solid:
    """Crea un engranaje base simplificado."""
    # Base cilíndrica
    base = cylinder(radius=radius, height=thickness)
    
    # Dientes (restados)
    tooth_depth = 3.0
    cutter = box(width=4.0, height=thickness + 2, depth=5.0)
    
    # Movemos el cortador al borde
    cutter_moved = translate(x=radius)(cutter)
    
    # Acumulamos los cortes
    full_gear = base
    angle_step = 360.0 / teeth
    
    for i in range(teeth):
        # Rotamos el cortador
        angle = i * angle_step
        rotated_cutter = rotate(axis='z', degrees=angle)(cutter_moved)
        # Restamos el diente
        full_gear = difference(full_gear, rotated_cutter)
        
    return full_gear

# --- 3. EJECUCIÓN PRINCIPAL ---

if __name__ == '__main__':
    print("⚙️ Iniciando Generador de Engranaje con Imagen...")

    # Rutas de archivos
    current_dir = os.path.dirname(__file__)
    project_root = os.path.dirname(current_dir)
    img_path = os.path.join(project_root, 'models', 'Star.png')
    out_path = os.path.join(project_root, 'models', 'Star_Gear.stl')

    try:
        # A. Cargar Imagen
        print(f"1. Leyendo imagen: {img_path}")
        mask = load_image_as_mask(img_path)
        
        # B. Crear Sólido de la Imagen (La Estrella)
        # Tamaño: 10x10, Grosor: 8 (para asegurar que corte bien)
        star_3d = image_solid(mask, width=10, height=10, thickness=8)
        
        # C. Crear Engranaje
        print("2. Generando geometría del engranaje...")
        gear = create_simple_gear(radius=15, thickness=5, teeth=10)

        # D. Combinar (Engranaje - Estrella)
        # Movemos la estrella un poco hacia arriba si queremos que sea un grabado superficial,
        # o la dejamos en el centro para que sea un agujero pasante.
        print("3. Aplicando operación booleana (Grabado)...")
        final_object = difference(gear, star_3d)

        # E. Exportar
        print(f"4. Exportando a STL (esto puede tardar unos segundos)...")
        # Resolution 80 es un buen balance. Si sale pixelado, sube a 100-120.
        export_stl(final_object, out_path, resolution=80)
        
        print(f"✅ ¡ÉXITO! Modelo guardado en: {out_path}")

    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}")
        print("Asegúrate de que 'Star.png' esté en la carpeta 'models' y tengas 'Pillow' instalado.")