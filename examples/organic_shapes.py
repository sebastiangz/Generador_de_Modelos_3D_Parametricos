import os
import sys
import numpy as np
import math

# Ajustar path para importar src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.vectors import Vector3
from src.curves import nurbs_curve
from src.surfaces import surface_of_revolution
from src.export import export_surface_stl

def create_organic_vase_profile():
    """
    Define una curva NURBS que servirá como la silueta del florero.
    Retorna una función que para un t (0 a 1) devuelve un Vector3.
    """
    # 1. PUNTOS DE CONTROL (La forma aproximada)
    # Imaginamos el perfil en el plano XZ (X=Radio, Z=Altura)
    control_points = [
        Vector3(0, 0, 0),     # Centro de la base
        Vector3(10, 0, 0),    # Borde de la base (plana)
        Vector3(15, 0, 5),    # Curva suave hacia arriba
        Vector3(8, 0, 15),    # Cintura estrecha
        Vector3(12, 0, 25),   # Se ensancha de nuevo
        Vector3(5, 0, 30)     # Boca del florero
    ]

    # 2. NUDOS (KNOTS)
    # Controlan cómo fluye la curva. Para grado 3, necesitamos len(points) + grado + 1 nudos.
    degree = 3
    n_points = len(control_points)
    # Vector de nudos "clamped" (empieza con 0s y termina con 1s para tocar los extremos)
    knots = [0.0, 0.0, 0.0, 0.0, 0.33, 0.66, 1.0, 1.0, 1.0, 1.0]

    # 3. PESOS (WEIGHTS)
    # Si aumentamos un peso, la curva es "atraída" más fuerte hacia ese punto.
    # Usamos 1.0 para estándar, pero variamos la cintura para acentuarla.
    weights = [1.0, 1.0, 1.0, 2.0, 1.0, 1.0] 

    # Creamos la función de la curva
    return nurbs_curve(control_points, knots, weights, degree)

def get_curve_2d_adapter(curve_3d_fn):
    """
    Adapta la función curva 3D para que sea compatible con surface_of_revolution.
    surface_of_revolution espera: (u) -> (radio, altura)
    """
    def adapter(u):
        vec = curve_3d_fn(u)
        # Usamos X como radio y Z como altura
        return (vec.x, vec.z)
    return adapter

if __name__ == '__main__':
    print("🏺 Generando Forma Orgánica (Florero NURBS)...")

    # 1. Crear el perfil curvo
    # Esto es matemática pura definiendo una silueta suave
    print("1. Calculando curva NURBS...")
    vase_curve = create_organic_vase_profile()

    # 2. Convertir a función de revolución
    # Adaptamos la curva para decir: "A tal avance (u), este es el radio y la altura"
    profile_2d = get_curve_2d_adapter(vase_curve)

    # 3. Crear la superficie matemática
    # Rotamos ese perfil alrededor del eje Z
    print("2. Generando superficie de revolución...")
    vase_surface = surface_of_revolution(profile_2d, axis='z')

    # 4. Exportar
    # Aquí ocurre la magia: el exportador recorrerá u (perfil) y v (rotación)
    # creando miles de triángulos para formar la malla suave.
    output_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'organic_vase.stl')
    print(f"3. Exportando a {output_path}...")
    
    export_surface_stl(
        vase_surface, 
        output_path, 
        u_steps=50,  # Calidad vertical (más alto = curva más suave)
        v_steps=60   # Calidad radial (más alto = círculo más perfecto)
    )

    print("✅ ¡Listo! Abre el archivo para ver las curvas suaves.")