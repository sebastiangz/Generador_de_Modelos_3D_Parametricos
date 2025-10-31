# 🎨 Proyecto 6: Generador de Modelos 3D Paramétricos

## 📋 Descripción del Proyecto

Sistema funcional para generar modelos 3D paramétricos mediante álgebra lineal funcional, operaciones CSG (Constructive Solid Geometry), transformaciones composables y exportación a formatos estándar (STL, OBJ).

**Universidad de Colima - Ingeniería en Computación Inteligente**  
**Materia**: Programación Funcional  
**Profesor**: Gonzalez Zepeda Sebastian  
**Semestre**: Agosto 2025 - Enero 2026{

**Colaboradores**: Eduardo David Ochoa Alvarez    Carlos Aaron Ramirez Vilchis  Victor Leonardo Hernandez Dominguez

---

## 🎯 Objetivos

- Implementar **álgebra lineal funcional** (vectores, matrices, transformaciones)
- Desarrollar **operaciones CSG** puras (union, difference, intersection)
- Crear **curvas y superficies** mediante funciones paramétricas
- Aplicar **transformaciones composables** (rotación, traslación, escala)
- Generar **meshes** mediante funciones puras
- Exportar modelos en formatos estándar

---

## 🛠️ Tecnologías Utilizadas

- **Lenguaje**: Python 3.11+
- **Paradigma**: Programación Funcional
- **Librerías**:
  - `numpy` - Álgebra lineal
  - `trimesh` - Manipulación de meshes
  - `numpy-stl` - Exportación STL
  - `pyvista` - Visualización 3D
  - `scipy` - Operaciones matemáticas

---

## 📦 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/3d-parametric-generator.git
cd 3d-parametric-generator

# Crear entorno virtual
python -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### requirements.txt
```
numpy>=1.24.0
trimesh>=4.0.0
numpy-stl>=3.0.0
pyvista>=0.43.0
scipy>=1.11.0
matplotlib>=3.7.0
toolz>=0.12.0
```

---

## 🚀 Uso del Sistema

```python
from src.geometry import sphere, box, cylinder
from src.transforms import rotate, translate, scale
from src.csg import union, difference, intersection
from toolz import compose

# Crear primitivas geométricas
base = box(width=10, height=2, depth=10)
hole = cylinder(radius=3, height=3)

# Operaciones CSG funcionales
part = difference(
    base,
    translate(hole, z=1)
)

# Transformaciones composables
transform = compose(
    scale(2.0),
    rotate(axis='z', degrees=45),
    translate(x=5, y=3)
)

final_model = transform(part)

# Exportar
export_stl(final_model, 'output.stl')
```

---

## 📂 Estructura del Proyecto

```
3d-parametric-generator/
├── src/
│   ├── __init__.py
│   ├── geometry.py         # Primitivas geométricas
│   ├── vectors.py          # Álgebra vectorial funcional
│   ├── transforms.py       # Transformaciones 3D
│   ├── csg.py             # Constructive Solid Geometry
│   ├── curves.py          # Curvas paramétricas
│   ├── surfaces.py        # Superficies paramétricas
│   ├── mesh.py            # Generación de meshes
│   └── export.py          # Exportación (STL, OBJ)
├── tests/
│   ├── test_geometry.py
│   ├── test_transforms.py
│   └── test_csg.py
├── examples/
│   ├── gears.py           # Generador de engranajes
│   ├── architecture.py    # Modelos arquitectónicos
│   └── organic_shapes.py  # Formas orgánicas
├── models/                # Modelos generados
├── docs/
│   ├── math_reference.md
│   └── api_guide.md
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🔑 Características Principales

### 1. Álgebra Lineal Funcional
```python
from dataclasses import dataclass
from typing import Callable
import numpy as np

@dataclass(frozen=True)
class Vector3:
    """Vector 3D inmutable"""
    x: float
    y: float
    z: float
    
    def dot(self, other: 'Vector3') -> float:
        """Producto punto"""
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other: 'Vector3') -> 'Vector3':
        """Producto cruz"""
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def map(self, fn: Callable[[float], float]) -> 'Vector3':
        """Aplicar función a cada componente"""
        return Vector3(fn(self.x), fn(self.y), fn(self.z))
    
    def magnitude(self) -> float:
        """Magnitud del vector"""
        return (self.x**2 + self.y**2 + self.z**2)**0.5

@dataclass(frozen=True)
class Matrix4x4:
    """Matriz de transformación 4x4 inmutable"""
    data: tuple  # 16 elementos
    
    def multiply(self, other: 'Matrix4x4') -> 'Matrix4x4':
        """Multiplicación de matrices"""
        a = np.array(self.data).reshape(4, 4)
        b = np.array(other.data).reshape(4, 4)
        result = np.matmul(a, b)
        return Matrix4x4(tuple(result.flatten()))
    
    def apply_to_vector(self, v: Vector3) -> Vector3:
        """Aplicar transformación a vector"""
        m = np.array(self.data).reshape(4, 4)
        vec = np.array([v.x, v.y, v.z, 1.0])
        result = np.matmul(m, vec)
        return Vector3(result[0], result[1], result[2])
```

### 2. Transformaciones Composables
```python
from functools import partial
from toolz import compose
import numpy as np

def rotation_matrix(axis: str, degrees: float) -> Matrix4x4:
    """Crear matriz de rotación funcional"""
    rad = np.radians(degrees)
    cos, sin = np.cos(rad), np.sin(rad)
    
    matrices = {
        'x': [1, 0, 0, 0,
              0, cos, -sin, 0,
              0, sin, cos, 0,
              0, 0, 0, 1],
        'y': [cos, 0, sin, 0,
              0, 1, 0, 0,
              -sin, 0, cos, 0,
              0, 0, 0, 1],
        'z': [cos, -sin, 0, 0,
              sin, cos, 0, 0,
              0, 0, 1, 0,
              0, 0, 0, 1]
    }
    return Matrix4x4(tuple(matrices[axis]))

def translation_matrix(x=0, y=0, z=0) -> Matrix4x4:
    """Crear matriz de traslación"""
    return Matrix4x4((
        1, 0, 0, x,
        0, 1, 0, y,
        0, 0, 1, z,
        0, 0, 0, 1
    ))

def scale_matrix(sx=1, sy=1, sz=1) -> Matrix4x4:
    """Crear matriz de escala"""
    return Matrix4x4((
        sx, 0, 0, 0,
        0, sy, 0, 0,
        0, 0, sz, 0,
        0, 0, 0, 1
    ))

# Composición de transformaciones
transform_pipeline = compose(
    partial(rotation_matrix, 'z', 45),
    partial(translation_matrix, x=5),
    partial(scale_matrix, sx=2, sy=2, sz=2)
)
```

### 3. Operaciones CSG Funcionales
```python
from dataclasses import dataclass
from typing import Callable, List

@dataclass(frozen=True)
class Solid:
    """Sólido 3D representado funcionalmente"""
    contains: Callable[[Vector3], bool]  # Función característica
    bounds: tuple  # (min_point, max_point)
    
    def transform(self, matrix: Matrix4x4) -> 'Solid':
        """Aplicar transformación al sólido"""
        inv_matrix = matrix.inverse()
        def new_contains(point: Vector3) -> bool:
            # Transformar punto al espacio original
            original_point = inv_matrix.apply_to_vector(point)
            return self.contains(original_point)
        return Solid(new_contains, self.bounds)

def union(solid1: Solid, solid2: Solid) -> Solid:
    """Unión booleana de dos sólidos"""
    def contains(point: Vector3) -> bool:
        return solid1.contains(point) or solid2.contains(point)
    return Solid(contains, combine_bounds(solid1.bounds, solid2.bounds))

def intersection(solid1: Solid, solid2: Solid) -> Solid:
    """Intersección booleana"""
    def contains(point: Vector3) -> bool:
        return solid1.contains(point) and solid2.contains(point)
    return Solid(contains, intersect_bounds(solid1.bounds, solid2.bounds))

def difference(solid1: Solid, solid2: Solid) -> Solid:
    """Diferencia booleana (solid1 - solid2)"""
    def contains(point: Vector3) -> bool:
        return solid1.contains(point) and not solid2.contains(point)
    return Solid(contains, solid1.bounds)
```

### 4. Curvas Paramétricas
```python
from typing import Callable

def parametric_curve(
    x: Callable[[float], float],
    y: Callable[[float], float],
    z: Callable[[float], float]
) -> Callable[[float], Vector3]:
    """Crear curva paramétrica funcional"""
    def curve(t: float) -> Vector3:
        return Vector3(x(t), y(t), z(t))
    return curve

# Ejemplo: hélice
def helix(radius: float, pitch: float):
    return parametric_curve(
        x=lambda t: radius * np.cos(t),
        y=lambda t: radius * np.sin(t),
        z=lambda t: pitch * t
    )

# Generar puntos de la curva
helix_curve = helix(radius=5, pitch=2)
points = [helix_curve(t) for t in np.linspace(0, 4*np.pi, 100)]
```

---

## 📊 Funcionalidades Implementadas

### Primitivas Geométricas
- ✅ Esfera, cubo, cilindro, cono
- ✅ Torus, prismas, pirámides
- ✅ Poliedros regulares

### Transformaciones
- ✅ Rotación (Euler, quaternions)
- ✅ Traslación, escala
- ✅ Reflexión, shear
- ✅ Composición de transformaciones

### CSG
- ✅ Union, difference, intersection
- ✅ Operaciones n-arias
- ✅ Smoothing de transiciones

### Curvas y Superficies
- ✅ Bézier, B-splines
- ✅ NURBS básicos
- ✅ Superficies de revolución
- ✅ Lofting funcional

### Exportación
- ✅ STL (ASCII y Binary)
- ✅ OBJ con materiales
- ✅ PLY para point clouds

---

## 🧪 Testing

```bash
# Tests
pytest tests/ -v

# Tests de geometría
pytest tests/test_geometry.py

# Tests de CSG
pytest tests/test_csg.py -v

# Benchmarks
pytest tests/ -k "benchmark"
```

---

## 📈 Pipeline de Desarrollo

### Semana 1: Geometría Básica (30 Oct - 5 Nov)
- Álgebra lineal funcional
- Primitivas geométricas
- Transformaciones básicas

### Semana 2: CSG (6 Nov - 12 Nov)
- Operaciones booleanas
- Composición de sólidos
- Optimización

### Semana 3: Curvas Paramétricas (13 Nov - 19 Nov)
- Curvas de Bézier
- Superficies paramétricas
- Generación de meshes

### Semana 4: Exportación (20 Nov)
- Exportación STL/OBJ
- Visualización
- Documentación

---

## 💼 Componente de Emprendimiento

**Aplicación Real**: Generador de modelos 3D para impresión 3D personalizada

**Propuesta de Valor**:
- Generación paramétrica de productos customizables
- API para integración con e-commerce
- Exportación directa a formatos de impresión
- Visualización 3D en navegador

**Casos de Uso**:
- **Joyería**: Anillos y pendientes parametrizables
- **Arquitectura**: Maquetas automáticas
- **Ingeniería**: Piezas mecánicas customizadas
- **Arte**: Esculturas generativas

---

## 📚 Referencias

- Foley et al. (1996). *Computer Graphics: Principles and Practice*
- **Trimesh Documentation**: https://trimsh.org/
- **PyVista**: https://docs.pyvista.org/
- **OpenSCAD CSG**: https://en.wikibooks.org/wiki/OpenSCAD_User_Manual
- **Objetos 3D para impresoras**: https://www.thingiverse.com

---

## 🏆 Criterios de Evaluación

- **Álgebra Lineal Funcional (25%)**: Corrección matemática, inmutabilidad
- **CSG (30%)**: Operaciones correctas, eficiencia
- **Parametrización (20%)**: Flexibilidad, elegancia
- **Exportación y Visualización (25%)**: Formatos correctos, calidad visual

---

## 👥 Autor

**Nombre**: [Tu Nombre]  
**Email**: [tu-email@ucol.mx]  
**GitHub**: [@tu-usuario](https://github.com/tu-usuario)

---

## 📄 Licencia

Proyecto académico - Universidad de Colima © 2025
