import os
import sys
from functools import reduce

# --- IMPORTACIONES ---
# Al estar en la raíz, podemos importar 'src' directamente sin trucos de path
from src.vectors import Vector3
from src.geometry import box, cylinder, pyramid
from src.transforms import translate, rotate, scale
from src.csg import union, difference, Solid
from src.export import export_stl

# ==========================================
# 1. LÓGICA DE CONSTRUCCIÓN (MOTORES)
# ==========================================

def create_floor_segment(width: float, height: float) -> Solid:
    """Crea un módulo de piso con columnas."""
    slab = box(width, height, width)
    col_radius = width * 0.08
    col_height = height * 3 
    col_offset = width / 2.0 - col_radius
    column = cylinder(col_radius, col_height)
    
    # Posicionar 4 columnas
    c1 = translate(x=col_offset, y=col_offset)(column)
    c2 = translate(x=-col_offset, y=col_offset)(column)
    c3 = translate(x=col_offset, y=-col_offset)(column)
    c4 = translate(x=-col_offset, y=-col_offset)(column)
    
    return reduce(union, [slab, c1, c2, c3, c4])

def build_twisted_tower(floors: int, width: float, height: float, twist: float) -> Solid:
    """Genera la Torre Giratoria."""
    generated_floors = []
    base_floor = create_floor_segment(width, height)
    
    for i in range(floors):
        elevation = i * height * 1.2
        rotation = i * twist
        
        # Transformación compuesta: Rotar y luego Subir
        transform = translate(z=elevation)
        rot = rotate(axis='z', degrees=rotation)
        
        # Aplicar al piso base
        current_floor = transform(rot(base_floor))
        generated_floors.append(current_floor)
    
    return reduce(union, generated_floors)

def build_step_pyramid(levels: int, base_width: float, level_height: float) -> Solid:
    """Genera la Pirámide Escalonada (Ziggurat)."""
    generated_levels = []
    
    for i in range(levels):
        elevation = i * level_height
        # Reducción progresiva del ancho
        current_width = base_width * (1 - (i / (levels + 1)))
        
        block = box(current_width, level_height, current_width)
        moved_block = translate(z=elevation)(block)
        generated_levels.append(moved_block)
        
    return reduce(union, generated_levels)

# ==========================================
# 2. INTERFAZ DE USUARIO (CLI)
# ==========================================

def get_input_number(prompt: str, default_val: float, type_fn=float):
    """Función auxiliar para pedir datos al usuario."""
    try:
        user_input = input(f"   > {prompt} [Default: {default_val}]: ")
        if not user_input:
            return default_val
        return type_fn(user_input)
    except ValueError:
        print("   ⚠️ Entrada inválida. Usando valor por defecto.")
        return default_val

def main():
    print("\n" + "="*50)
    print("   🏙️  GENERADOR DE ARQUITECTURA PARAMÉTRICA v1.0")
    print("       Universidad de Colima - Ingeniería")
    print("="*50)

    # Asegurar que existe la carpeta models
    models_dir = os.path.join(os.path.dirname(__file__), 'models')
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)

    while True:
        print("\n   ¿Qué deseas construir hoy?")
        print("   1. 🌪️  Torre Giratoria (Twisted Tower)")
        print("   2. 🏯  Pirámide Escalonada (Ziggurat)")
        print("   3. ❌  Salir")
        
        opcion = input("\n   Elige una opción (1-3): ")

        if opcion == '3':
            print("\n   👋 ¡Programa finalizado!")
            break

        model = None
        filename = "output.stl"

        if opcion == '1':
            print("\n   --- Configuración de Torre ---")
            pisos = get_input_number("Número de pisos", 25, int)
            ancho = get_input_number("Ancho del piso", 12.0)
            giro = get_input_number("Grados de giro", 5.0)
            
            print("\n   ⚙️  Procesando geometría...")
            model = build_twisted_tower(pisos, ancho, 2.0, giro)
            filename = "torre_generada.stl"

        elif opcion == '2':
            print("\n   --- Configuración de Pirámide ---")
            niveles = get_input_number("Niveles", 10, int)
            base = get_input_number("Ancho base", 30.0)
            
            print("\n   ⚙️  Procesando geometría...")
            model = build_step_pyramid(niveles, base, 3.0)
            filename = "piramide_generada.stl"

        else:
            print("   ⚠️ Opción no válida.")
            continue

        # Preguntar nombre
        user_name = input(f"   💾 Nombre del archivo (Enter para '{filename}'): ")
        if user_name:
            if not user_name.lower().endswith('.stl'):
                user_name += '.stl'
            filename = user_name

        # Exportar
        output_path = os.path.join(models_dir, filename)
        print(f"   ⏳ Exportando a STL (Alta Calidad)... Por favor espera.")
        
        # Usamos resolución 150 para buena calidad
        export_stl(model, output_path, resolution=150)
        
        print(f"\n   ✅ ¡LISTO! Archivo guardado en:\n      {output_path}")
        input("   Presiona Enter para continuar...")

if __name__ == '__main__':
    main()