import os
import sys
import time
import random
from functools import reduce

# --- IMPORTACIONES DEL MOTOR (CORE) ---
from src.vectors import Vector3
from src.geometry import box, cylinder, cone, pyramid, sphere
from src.transforms import translate, rotate, scale, scale_uniform
from src.csg import union, difference, intersection, Solid
from src.export import export_stl
from examples.architecture import build_twisted_tower # Reutilizamos tu tecnología de edificios

# ==============================================================================
# 🏭 MÓDULO DE GENERACIÓN PROCEDURAL (ASSET FACTORY)
# ==============================================================================

def generate_lowpoly_tree(height: float, foliage_width: float, layers: int) -> Solid:
    """
    Genera un árbol estilo 'Low Poly' ideal para juegos móviles o indie.
    Variación: Cambia la altura y ancho para crear bosques diversos.
    """
    # 1. Tronco
    trunk_h = height * 0.3
    trunk_r = foliage_width * 0.15
    trunk = cylinder(radius=trunk_r, height=trunk_h)
    
    parts = [trunk]
    
    # 2. Follaje (Capas de conos)
    foliage_start_h = trunk_h * 0.8
    layer_height = (height - foliage_start_h) / layers
    
    for i in range(layers):
        # Cada capa es un poco más pequeña que la anterior
        current_w = foliage_width * (1 - (i * 0.15))
        current_h = layer_height * 2.5 # Solapamiento para que se vea denso
        
        foliage = cone(radius=current_w, height=current_h)
        
        # Subir el follaje
        elevation = foliage_start_h + (i * layer_height * 0.8)
        foliage_moved = translate(z=elevation)(foliage)
        parts.append(foliage_moved)
        
    return reduce(union, parts)

def generate_loot_crate(size: float, indent_factor: float = 0.8) -> Solid:
    """
    Genera una caja de suministros (Loot Box) Sci-Fi.
    Usa sustracción booleana para crear paneles tecnológicos.
    """
    # Caja Base
    base = box(size, size, size)
    
    # Cortadores (para hacer los huecos en las caras)
    cut_size = size * indent_factor
    cutter = box(cut_size, cut_size, size * 1.2) # Largo extra para cortar bien
    
    # Cortar en 3 ejes
    c_z = cutter
    c_y = rotate(axis='x', degrees=90)(cutter)
    c_x = rotate(axis='y', degrees=90)(cutter)
    
    # Núcleo interno (para que no quede hueca del todo)
    core_size = size * 0.9
    core = box(core_size, core_size, core_size)
    
    # Operación: (Base - Cortes) + Núcleo
    frame = difference(difference(difference(base, c_z), c_y), c_x)
    
    return union(frame, core)

def generate_energy_crystal(height: float, width: float) -> Solid:
    """
    Genera un cristal de energía asimétrico.
    Ideal para objetivos de misión o decoración de cuevas.
    """
    # Base del cristal (dos pirámides pegadas por la base)
    top = pyramid(width, width, height/2)
    bottom = pyramid(width, width, height/2)
    
    # Rotar la de abajo para que apunte al suelo
    bottom_flipped = rotate(axis='x', degrees=180)(bottom)
    
    # Unirlas
    crystal_base = union(translate(z=height/4)(top), translate(z=-height/4)(bottom_flipped))
    
    # Añadir "imperfecciones" (cristales satélite) para realismo
    shard = scale_uniform(0.4)(crystal_base)
    shard1 = translate(x=width*0.5, z=-height*0.2)(rotate(axis='z', degrees=45)(shard))
    shard2 = translate(x=-width*0.5, z=height*0.1)(rotate(axis='y', degrees=30)(shard))
    
    return reduce(union, [crystal_base, shard1, shard2])

# ==============================================================================
# 🖥️ INTERFAZ DE USUARIO (CLI) - ENFOQUE DE PRODUCTO
# ==============================================================================

def get_input(prompt, default, type_fn=float):
    try:
        val = input(f"   🔹 {prompt} [Def: {default}]: ")
        return type_fn(val) if val else default
    except:
        return default

def main():
    # Branding del Producto
    print("\n" + "█"*60)
    print("   ⚔️  ASSET FORGE PRO  v1.0")
    print("   Generador Procedural de Assets para Videojuegos")
    print("   Licencia: INDIE DEVELOPER (Free Tier)")
    print("█"*60)

    # Crear carpeta de salida
    output_dir = os.path.join(os.path.dirname(__file__), 'game_assets')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    while True:
        print("\n   📂 LIBRERÍA DE GENERADORES:")
        print("   1. 🌲 Árbol Low Poly (Environment)")
        print("   2. 📦 Caja Sci-Fi (Prop/Loot)")
        print("   3. 💎 Cristal de Energía (Objective)")
        print("   4. 🏙️ Rascacielos Cyberpunk (Background)")
        print("   5. 🚪 Salir")
        
        choice = input("\n   Selecciona Asset a forjar (1-5): ")
        
        if choice == '5':
            print("\n   💾 Guardando sesión... ¡A seguir desarrollando!")
            break

        asset = None
        name_default = "asset"
        
        if choice == '1':
            print("\n   --- Configuración de Vegetación ---")
            h = get_input("Altura del árbol", 6.0)
            w = get_input("Ancho del follaje", 3.0)
            l = get_input("Capas de hojas", 3, int)
            asset = generate_lowpoly_tree(h, w, l)
            name_default = "tree_lowpoly"
            
        elif choice == '2':
            print("\n   --- Configuración de Prop ---")
            s = get_input("Tamaño de la caja", 10.0)
            asset = generate_loot_crate(s)
            name_default = "loot_crate"
            
        elif choice == '3':
            print("\n   --- Configuración de Cristal ---")
            h = get_input("Altura del cristal", 8.0)
            w = get_input("Ancho", 3.0)
            asset = generate_energy_crystal(h, w)
            name_default = "crystal_shard"
            
        elif choice == '4':
            print("\n   --- Configuración Urbana ---")
            f = get_input("Número de pisos", 15, int)
            t = get_input("Torsión (Twist)", 5.0)
            asset = build_twisted_tower(f, 10.0, 2.0, t)
            name_default = "building_cyberpunk"
            
        else:
            continue

        # --- SISTEMA DE LOD (Level of Detail) ---
        # Esto cumple con la propuesta de "Optimización"
        print("\n   🎮 SELECCIONA LOD (Nivel de Detalle):")
        print("   [L] LOD 0 - Mobile/Web (Rápido, Low Poly) -> Res: 40")
        print("   [M] LOD 1 - Console/PC (Balanceado)       -> Res: 100")
        print("   [H] LOD 2 - Cinematic (Ultra Detalle)     -> Res: 200")
        
        lod_choice = input("   Opción [L/M/H] (Default M): ").upper()
        
        resolution = 100
        tag = "LOD1"
        
        if lod_choice == 'L': 
            resolution = 40
            tag = "LOD0"
        elif lod_choice == 'H': 
            resolution = 200
            tag = "LOD2"
            
        # Exportar
        filename = input(f"   📝 Nombre del archivo (Enter para '{name_default}'): ")
        if not filename: filename = name_default
        
        # Añadimos el tag de LOD al nombre automáticamente (buena práctica en gamedev)
        full_name = f"{filename}_{tag}.stl"
        path = os.path.join(output_dir, full_name)
        
        print(f"\n   🔨 Forjando Asset ({tag})...")
        t_start = time.time()
        
        export_stl(asset, path, resolution=resolution)
        
        t_end = time.time()
        print(f"   ✅ ASSET CREADO: {path}")
        print(f"      Tiempo de render: {t_end - t_start:.2f}s")
        print("      Listo para importar en Unity/Unreal Engine.")

if __name__ == '__main__':
    main()