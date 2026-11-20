#  Guía de la API — Detector de Armas con Modelo 3D

Este documento describe la interfaz de programación (API) de los módulos puros desarrollados bajo el paradigma de **Programación Funcional** en Python. Todas las estructuras de datos son inmutables (`tuple`) y las funciones carecen de efectos secundarios internos.

---

## 1. `algebra_lineal.py`
Define los tipos de datos geométricos base y las operaciones vectoriales y matriciales en coordenadas homogéneas ($4 \times 4$).

### Tipos Inmutables
* `Vertice = tuple[float, float, float]`
* `Triangulo = tuple[Vertice, Vertice, Vertice]`
* `Malla = tuple[Triangulo, ...]`
* `Matriz4x4 = tuple[tuple[float, float, float, float], ...]`

### Funciones Principales
* **`sumar_vectores(u: Vertice, v: Vertice) -> Vertice`**  
  Retorna la suma componente a componente de dos vectores 3D.
* **`restar_vectores(u: Vertice, v: Vertice) -> Vertice`**  
  Retorna el vector diferencia $\vec{u} - \vec{v}$.
* **`producto_punto(u: Vertice, v: Vertice) -> float`**  
  Calcula el producto escalar entre $\vec{u}$ y $\vec{v}$.
* **`producto_cruz(u: Vertice, v: Vertice) -> Vertice`**  
  Calcula el vector perpendicular resultante $\vec{u} \times \vec{v}$.
* **`calcular_normal_triangulo(tri: Triangulo) -> Vertice`**  
  Obtiene el vector normal unitario de una cara triangular.
* **`multiplicar_matrices(a: Matriz4x4, b: Matriz4x4) -> Matriz4x4`**  
  Multiplica dos matrices afines de $4 \times 4$ de manera pura.
* **`aplicar_matriz_a_vertice(m: Matriz4x4, v: Vertice) -> Vertice`**  
  Transforma un vértice 3D utilizando coordenadas homogéneas $(x, y, z, 1)$.
* **`calcular_bounding_box(malla: Malla) -> tuple[Vertice, Vertice]`**  
  Calcula los puntos extremos `(v_min, v_max)` de la caja envolvente alineada a los ejes (AABB).
* **`calcular_dimensiones(malla: Malla) -> Vertice`**  
  Retorna el ancho ($\Delta x$), alto ($\Delta y$) y largo ($\Delta z$) del modelo.

---

## 2. `transformaciones.py`
Provee herramientas de composición funcional y matrices de transformación afín para normalizar modelos 3D antes de su evaluación.

### Funciones Principales
* **`compose(*funciones: Transformacion) -> Transformacion`**  
  Operador de orden superior que encadena múltiples transformaciones $f_1(f_2(\dots f_n(v)))$ en una sola función pura.
* **`componer_matrices(*matrices: Matriz4x4) -> Matriz4x4`**  
  Combina una secuencia de matrices $4 \times 4$ mediante multiplicación asociativa.
* **`matriz_traslacion(tx: float, ty: float, tz: float) -> Matriz4x4`**  
  Genera la matriz homogénea de desplazamiento espacial.
* **`matriz_escalado(sx: float, sy: float, sz: float) -> Matriz4x4`**  
  Genera la matriz de escalado por eje.
* **`matriz_rotacion_x(radianes: float) -> Matriz4x4`** / **`_y`** / **`_z`**  
  Generan matrices de rotación elemental alrededor de los ejes cartesianos.
* **`normalizar_malla(malla: Malla) -> Malla`**  
  Pipeline completo que:
  1. Centra el modelo en el origen $(0,0,0)$.
  2. Alinea su dimensión más larga con el eje $Z$.
  3. Escala uniformemente la geometría dentro del cubo unitario $[-1, 1]^3$.

---

## 3. `geometria_parametrica.py`
Genera curvas y superficies analíticas discretizadas en mallas de triángulos para modelar componentes característicos.

### Funciones Principales
* **`curva_bezier_cubica(p0, p1, p2, p3) -> Callable[[float], Vertice]`**  
  Devuelve una función pura $B(t)$ con $t \in [0, 1]$ evaluada sobre cuatro puntos de control.
* **`teselar_superficie(superficie: SuperficieParametrica, pasos_u: int, pasos_v: int) -> Malla`**  
  Discretiza cualquier función paramétrica $S(u, v) \to (x, y, z)$ en una malla triangular cerrada.
* **`generar_canon_parametrico(radio: float, longitud: float) -> Malla`**  
  Modela un cañón cilíndrico alineado al eje $Z$.
* **`generar_empunadura_parametrica(ancho: float, grosor: float, alto: float) -> Malla`**  
  Extiende una sección elíptica ergonómica a lo largo de una curva de Bézier cúbica.
* **`generar_hoja_punzocortante(largo: float, ancho_base: float, grosor_lomo: float) -> Malla`**  
  Genera una hoja simétrica de doble filo que converge parabólicamente hacia la punta.

---

## 4. `csg.py`
Implementa **Geometría Constructiva de Sólidos (CSG)** mediante Campos de Distancia con Signo (**SDF**, *Signed Distance Functions*).

### Funciones Principales
* **`union(solido_a: SDF, solido_b: SDF) -> SDF`**  
  Operación booleana $A \cup B$ implementada como $\min(f_A(p), f_B(p))$.
* **`intersection(solido_a: SDF, solido_b: SDF) -> SDF`**  
  Operación booleana $A \cap B$ implementada como $\max(f_A(p), f_B(p))$.
* **`difference(solido_a: SDF, solido_b: SDF) -> SDF`**  
  Operación booleana $A \setminus B$ implementada como $\max(f_A(p), -f_B(p))$.
* **`malla_a_sdf(malla: Malla, resolucion_grid: int) -> SDF`**  
  Convierte una malla triangular normalizada en una función volumétrica continua $f: \mathbb{R}^3 \to \mathbb{R}$.
* **`calcular_iou_csg(solido_a: SDF, solido_b: SDF, resolucion: int) -> float`**  
  Calcula el índice de similitud volumétrica (IoU 3D) muestreando puntos en $[-1, 1]^3$.

---

## 5. `clasificador.py` y `io_meshes.py`
* **`cargar_stl(ruta: Path) -> Malla`** (`io_meshes.py`): Detecta automáticamente si el archivo STL es **binario** o **ASCII** y lo parsea a estructuras inmutables.
* **`exportar_stl(malla: Malla, ruta_salida: Path)`** / **`exportar_obj(...)`** (`io_meshes.py`): Serializan la malla normalizada en formatos estándar.
* **`evaluar_similitud_csg(malla_desconocida: Malla, malla_referencia: Malla) -> float`** (`clasificador.py`): Combina la coincidencia volumétrica CSG ($65\%$) y la similitud de proporciones espaciales ($35\%$) para emitir un puntaje final en $[0.0, 1.0]$.