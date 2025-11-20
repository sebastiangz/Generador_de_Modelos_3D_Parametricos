"""
organic_shapes.py

Generador de formas orgánicas usando curvas y superficies paramétricas.
Demuestra:
- Uso de NURBS (Non-Uniform Rational B-Splines) para el perfil 2D.
- Uso de Surface of Revolution (Superficie de Revolución).
"""

from src.vectors import Vector3
from src.curves import nurbs_curve
from src.mesh import mesh_from_surface
from src.curves import nurbs_curve, ParametricCurve # <-- AÑADIR ParametricCurve
from src.surfaces import surface_of_revolution, Curve2D # <-- AÑADIR Curve2D
import numpy as np
import math

def create_smooth_vase_profile() -> 'ParametricCurve':
    """
    Define la forma 2D (radio vs altura) usando una curva NURBS.
    Los puntos de control y pesos controlan la suavidad y el ensanchamiento.
    """
    # Puntos de control (solo en el plano XZ - radio y altura)
    # (x, y) = (radio, z)
    control_points = [
        Vector3(0, 0, -10),    # Base (radio 0, z=-10)
        Vector3(15, 0, -8),    # Hombro inferior (tira el perfil hacia afuera)
        Vector3(25, 0, 5),     # Cuerpo principal (más ancho)
        Vector3(15, 0, 18),    # Hombro superior
        Vector3(5, 0, 20)      # Boca (radio 5, z=20)
    ]

    # Vector de Nudos (Knots) - no uniforme para mayor control
    degree = 2 # Grado cuadrático
    num_points = len(control_points)
    num_knots = num_points + degree + 1
    
    # Crear un vector de nudos no uniforme (esto permite a NURBS modelar curvas complejas)
    knots = np.zeros(num_knots)
    knots[degree:num_points] = np.linspace(0, 1, num_points - degree)
    knots[num_points:] = 1.0
    
    # Pesos (Weights) - para hacer la curva "racional" (NURBS)
    # Pesos más altos 'jalan' la curva hacia ese punto
    weights = [1.0, 1.5, 1.0, 1.5, 1.0] 

    # Crear la curva NURBS
    return nurbs_curve(control_points, knots.tolist(), weights, degree)

def get_profile_fn(nurbs_fn: 'ParametricCurve') -> 'Curve2D':
    """
    Convierte la curva NURBS 3D (x, 0, z) en la función Curve2D (radio, altura).
    """
    def curve_2d(u: float) -> tuple[float, float]:
        # El parámetro 'u' de la superficie mapea a 't' de la curva
        point = nurbs_fn(u)
        # (radio, altura)
        return (point.x, point.z) 
    return curve_2d

# --- USO ---
if __name__ == '__main__':
    from src.export import export_surface_stl
    
    # 1. Crear la curva de perfil NURBS
    nurbs_profile = create_smooth_vase_profile()
    
    # 2. Obtener la función (radio, altura)
    profile_fn = get_profile_fn(nurbs_profile)
    
    # 3. Crear la Superficie de Revolución rotando el perfil alrededor del eje Z
    vase_surface_fn = surface_of_revolution(profile_fn, axis='z')

    print("Generando superficie paramétrica...")
    # 4. Exportar a STL usando el generador de mallas de superficie
    export_surface_stl(
        vase_surface_fn, 
        'models/organic_vase.stl', 
        u_steps=60, # Resolución a lo largo del perfil
        v_steps=60  # Resolución alrededor del eje de rotación
    )
    print("Florero orgánico exportado a models/organic_vase.stl")