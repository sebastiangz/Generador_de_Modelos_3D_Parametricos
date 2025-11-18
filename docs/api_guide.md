# Guía de API: Biblioteca CSG Funcional

Esta guía documenta la API de la biblioteca de Geometría Constructiva de Sólidos (CSG) funcional.

El enfoque de esta biblioteca es **funcional e inmutable**. Las primitivas geométricas (`Solid`) no se modifican. En su lugar, las operaciones (como `union` o `translate`) toman sólidos existentes y retornan un objeto `Solid` completamente nuevo.

## Tabla de Contenidos

* [1. Conceptos Básicos (`src.vectors`)](#vectores)
* [2. Primitivas Geométricas (`src.geometry`)](#geometria)
* [3. Transformaciones (`src.transforms`)](#transformaciones)
* [4. Operaciones CSG (`src.csg`)](#csg)
* [5. Curvas Paramétricas (`src.curves`)](#curvas)
* [6. Superficies Paramétricas (`src.surfaces`)](#superficies)
* [7. Exportación (`src.export`)](#exportacion)

---

<a name="vectores"></a>
## 1. Conceptos Básicos (`src.vectors`)

Este módulo proporciona las estructuras de datos fundamentales e inmutables.

### Vector3

Representa un vector 3D o un punto en el espacio. Es un `dataclass` inmutable.

* **Creación:** `v = Vector3(x, y, z)`
* **Atributos:**
    * `v.x` (float)
    * `v.y` (float)
    * `v.z` (float)
* **Operaciones:**
    * `v1 + v2`, `v1 - v2` (Suma/resta de vectores)
    * `v * escalar`, `v / escalar` (Multiplicación/división por escalar)
* **Métodos Principales:**
    * `v.dot(other: Vector3) -> float`: Producto punto.
    * `v.cross(other: Vector3) -> Vector3`: Producto cruz.
    * `v.magnitude() -> float`: Longitud del vector.
    * `v.normalize() -> Vector3`: Vector unitario en la misma dirección.

### Matrix4x4

Representa una matriz de transformación homogénea 4x4. Usada internamente por el módulo `transforms`, generalmente no necesitarás crearla manualmente.

---

<a name="geometria"></a>
## 2. Primitivas Geométricas (`src.geometry`)

Estas funciones crean objetos `Solid` básicos, todos centrados en el origen.

### `sphere(radius: float) -> Solid`

* **Descripción:** Crea una esfera sólida.
* **Parámetros:**
    * `radius` (float): El radio de la esfera. Debe ser positivo.
* **Implementación (de `src.geometry`):**
    ```python
    def sphere(radius: float) -> Solid:
        """Crea un Sólido esfera centrado en el origen"""
        if radius <= 0:
            raise ValueError("El radio debe ser positivo")

        def contains(point: Vector3) -> bool:
            # Un punto está dentro si su magnitud es <= al radio
            return point.magnitude() <= radius

        bounds: Bounds = (
            Vector3(-radius, -radius, -radius),
            Vector3(radius, radius, radius)
        )
        return Solid(contains, bounds)
    ```
* **Análisis de la Implementación:**
    * La función define una **función `contains` interna**. Esta es la "prueba" matemática que define la forma.
    * Para una esfera, la prueba es simple: un punto está "dentro" si su distancia al origen (`point.magnitude()`) es menor o igual al radio.
    * Crea los `bounds` (caja delimitadora) necesarios para las optimizaciones de CSG.
    * Finalmente, retorna un nuevo objeto `Solid`, pasando la función `contains` y los `bounds` a su constructor.

### `box(width: float, height: float, depth: float) -> Solid`

* **Descripción:** Crea una caja sólida (paralelepípedo).
* **Parámetros:**
    * `width` (float): Dimensión total en el eje X.
    * `height` (float): Dimensión total en el eje Y.
    * `depth` (float): Dimensión total en el eje Z.
* **Implementación (de `src.geometry`):**
    ```python
    def box(width: float, height: float, depth: float) -> Solid:
        """
        Crea un Sólido caja (cubo/paralelepípedo) centrado en el origen.
        """
        if any(d <= 0 for d in [width, height, depth]):
            raise ValueError("Las dimensiones deben ser positivas")

        w2, h2, d2 = width / 2.0, height / 2.0, depth / 2.0

        def contains(point: Vector3) -> bool:
            # Un punto está dentro si sus coordenadas absolutas
            # son menores o iguales a la mitad de las dimensiones.
            return (
                abs(point.x) <= w2 and
                abs(point.y) <= h2 and
                abs(point.z) <= d2
            )

        bounds: Bounds = (
            Vector3(-w2, -h2, -d2),
            Vector3(w2, h2, d2)
        )
        return Solid(contains, bounds)
    ```
* **Análisis de la Implementación:**
    * La lógica `contains` comprueba si el valor absoluto de cada componente del punto (`x`, `y`, `z`) es menor o igual a la mitad de la dimensión correspondiente (`w2`, `h2`, `d2`).
    * Esto funciona porque la caja está centrada en el origen.

### `cylinder(radius: float, height: float) -> Solid`

* **Descripción:** Crea un cilindro sólido, alineado con el eje Z.
* **Parámetros:**
    * `radius` (float): Radio del cilindro en el plano XY.
    * `height` (float): Altura total a lo largo del eje Z.
* **Implementación (de `src.geometry`):**
    ```python
    def cylinder(radius: float, height: float) -> Solid:
        """
        Crea un Sólido cilindro centrado en el origen,
        alineado con el eje Z.
        """
        if radius <= 0 or height <= 0:
            raise ValueError("El radio y la altura deben ser positivos")

        h2 = height / 2.0

        def contains(point: Vector3) -> bool:
            # Comprueba si está dentro del radio en el plano XY
            in_radius = (point.x**2 + point.y**2)**0.5 <= radius
            # Comprueba si está dentro de la altura en el eje Z
            in_height = abs(point.z) <= h2
            return in_radius and in_height

        bounds: Bounds = (
            Vector3(-radius, -radius, -h2),
            Vector3(radius, radius, h2)
        )
        return Solid(contains, bounds)
    ```
* **Análisis de la Implementación:**
    * La función `contains` se divide en dos pruebas lógicas `and`:
    * 1. `in_radius`: Comprueba la distancia 2D en el plano XY (ignorando Z) usando el teorema de Pitágoras.
    * 2. `in_height`: Comprueba que el punto esté dentro de los límites de Z.

### `cone(radius: float, height: float) -> Solid`

* **Descripción:** Crea un cono sólido, alineado con el eje Z, con la punta en `+Z`.
* **Parámetros:**
    * `radius` (float): Radio de la base en `Z = -height/2`.
    * `height` (float): Altura total a lo largo del eje Z.
* **Implementación (de `src.geometry`):**
    ```python
    def cone(radius: float, height: float) -> Solid:
        """
        Crea un Sólido cono centrado en el origen, alineado con el eje Z.
        """
        if radius <= 0 or height <= 0:
            raise ValueError("El radio y la altura deben ser positivos")

        h2 = height / 2.0

        def contains(point: Vector3) -> bool:
            if not abs(point.z) <= h2:
                return False

            # Interpolar linealmente el radio basado en la altura
            # En z = -h2, factor = 1.0 * radius
            # En z = +h2, factor = 0.0 * radius
            interp_factor = (h2 - point.z) / height
            radius_at_z = radius * interp_factor

            # Comprobar si está dentro del radio en esa "rebanada"
            return (point.x**2 + point.y**2)**0.5 <= radius_at_z
        ...
        return Solid(contains, bounds)
    ```
* **Análisis de la Implementación:**
    * Esta es una forma más avanzada. Primero, rechaza cualquier punto fuera de la altura.
    * Luego, calcula el radio que *debería* tener el cono en la altura `z` de ese punto. Esto se hace con una **interpolación lineal** (`interp_factor`).
    * Finalmente, realiza la misma prueba de radio 2D que el cilindro, pero usando el `radius_at_z` calculado.

### `torus(major_radius: float, minor_radius: float) -> Solid`

* **Descripción:** Crea un toro (donut) sólido, acostado sobre el plano XY.
* **Parámetros:**
    * `major_radius` (float): Radio desde el origen al centro del tubo.
    * `minor_radius` (float): Radio del tubo mismo.
* **Implementación (de `src.geometry`):**
    ```python
    def torus(major_radius: float, minor_radius: float) -> Solid:
        ...
        R, r = major_radius, minor_radius
        r_squared = r**2

        def contains(point: Vector3) -> bool:
            # ( (x^2 + y^2)^0.5 - R )^2 + z^2 <= r^2
            xy_dist = (point.x**2 + point.y**2)**0.5
            term_1 = (xy_dist - R)**2
            term_2 = point.z**2
            return (term_1 + term_2) <= r_squared
        ...
        return Solid(contains, bounds)
    ```
* **Análisis de la Implementación:**
    * Esta es la fórmula matemática de un toro.
    * `xy_dist` es la distancia 2D del punto al eje Z.
    * `xy_dist - R` es la distancia del punto al "centro del tubo".
    * `term_1` y `term_2` forman una prueba de Pitágoras 2D, pero en un plano "vertical" que corta el toro. Comprueba si la distancia al centro del tubo es menor o igual al radio menor (`r`).

### `pyramid(width: float, depth: float, height: float) -> Solid`

* **Descripción:** Crea una pirámide de base rectangular, alineada con el eje Z, con la punta en `+Z`.
* **Implementación (de `src.geometry`):**
    ```python
    def pyramid(width: float, depth: float, height: float) -> Solid:
        ...
        w2, d2, h2 = width / 2.0, depth / 2.0, height / 2.0

        def contains(point: Vector3) -> bool:
            if not abs(point.z) <= h2:
                return False

            # Interpolar linealmente el tamaño de la base
            interp_factor = (h2 - point.z) / height
            width_at_z = w2 * interp_factor
            depth_at_z = d2 * interp_factor

            return (abs(point.x) <= width_at_z) and (abs(point.y) <= depth_at_z)
        ...
        return Solid(contains, bounds)
    ```
* **Análisis de la Implementación:**
    * Funciona de forma idéntica al `cone`, pero en lugar de interpolar un `radius_at_z`, interpola un `width_at_z` y un `depth_at_z`.
    * La prueba final es una prueba de `box`, pero usando las dimensiones interpoladas.

---

<a name="transformaciones"></a>
## 3. Transformaciones (`src.transforms`)

Estas son **funciones de orden superior**. Retornan una función (`TransformFn`) que aplica la transformación.

### `translate(x: float = 0, y: float = 0, z: float = 0) -> TransformFn`

* **Descripción:** Retorna una función que aplica una traslación.
* **Parámetros:**
    * `x`, `y`, `z` (float): Distancia a mover en cada eje.
* **Implementación (de `src.transforms`):**
    ```python
    def translate(x: float = 0, y: float = 0, z: float = 0) -> TransformFn:
        """Retorna una función que aplica una traslación a un Sólido."""
        matrix = _translation_matrix(x, y, z)
        def apply_transform(solid: Solid) -> Solid:
            return solid.transform(matrix)
        return apply_transform
    ```
* **Análisis de la Implementación:**
    * Esta función sigue el **patrón de clausura (closure)**.
    * 1. Llama a `_translation_matrix` (una función privada) para obtener una `Matrix4x4` que representa la traslación.
    * 2. Define una función interna `apply_transform`.
    * 3. **Retorna** esa función interna. La función retornada "recuerda" la `matrix` que se creó.
    * 4. Cuando el usuario escribe `translate(5, 0, 0)(mi_solido)`, primero se ejecuta `translate`, que retorna `apply_transform`. Inmediatamente después, `apply_transform` se ejecuta, llamando a `mi_solido.transform(matrix)`.

### `rotate(axis: str, degrees: float) -> TransformFn`

* **Descripción:** Retorna una función que aplica una rotación (Euler).
* **Parámetros:**
    * `axis` (str): Eje de rotación. Debe ser `'x'`, `'y'`, o `'z'`.
    * `degrees` (float): Grados a rotar.
* **Implementación (de `src.transforms`):**
    ```python
    def rotate(axis: str, degrees: float) -> TransformFn:
        """Retorna una función que aplica una rotación (Euler) a un Sólido."""
        matrix = _rotation_matrix(axis, degrees)
        def apply_transform(solid: Solid) -> Solid:
            return solid.transform(matrix)
        return apply_transform
    ```
* **Análisis de la Implementación:**
    * Idéntica a `translate`, pero llama a `_rotation_matrix` para obtener la matriz de transformación.

### `scale(sx: float = 1, sy: float = 1, sz: float = 1) -> TransformFn`

* **Descripción:** Retorna una función que aplica una escala.
* **Parámetros:**
    * `sx`, `sy`, `sz` (float): Factor de escala en cada eje.
* **Implementación (de `src.transforms`):**
    ```python
    def scale(sx: float = 1, sy: float = 1, sz: float = 1) -> TransformFn:
        """Retorna una función que aplica una escala a un Sólido."""
        matrix = _scale_matrix(sx, sy, sz)
        def apply_transform(solid: Solid) -> Solid:
            return solid.transform(matrix)
        return apply_transform
    ```

### `reflect(plane: str) -> TransformFn`

* **Descripción:** Retorna una función que refleja (espejo) un sólido.
* **Parámetros:**
    * `plane` (str): El plano sobre el cual reflejar. Opciones: `'xy'`, `'xz'`, `'yz'`.
* **Implementación (de `src.transforms`):**
    ```python
    def reflect(plane: str) -> TransformFn:
        """
        Retorna una función que aplica una reflexión (espejo) a un Sólido.
        """
        matrix = _reflection_matrix(plane)
        def apply_transform(solid: Solid) -> Solid:
            return solid.transform(matrix)
        return apply_transform
    ```
* **Análisis de la Implementación:**
    * La función privada `_reflection_matrix` simplemente llama a `_scale_matrix` con un valor negativo en el eje perpendicular al plano. (Ej. reflejar en 'xy' es escalar Z por -1).

### Ejemplo de Uso (Transformaciones)

Puedes aplicar las transformaciones de dos maneras:

```python
from src.geometry import box
from src.transforms import translate, rotate
# Para composición avanzada, se usaría una utilidad como `toolz.compose`
# from toolz import compose

# --- Primitiva ---
caja = box(10, 10, 10)

# --- 1. Aplicación Directa ---
# La función `translate(5, 0, 0)` RETORNA una función,
# que luego llamamos con `(caja)`
caja_movida = translate(5, 0, 0)(caja)

# --- 2. Composición (Ejemplo conceptual con `compose`) ---
# Primero se define la secuencia de transformación
# (Se aplica de abajo hacia arriba: rotar, luego trasladar)
# transformacion = compose(
#     translate(10, 0, 0),
#     rotate('x', 45)
# )

# Luego se aplica la transformación compuesta al sólido
# caja_transformada = transformacion(caja)

# --- 3. Composición Manual (sin `toolz`) ---
caja_rotada = rotate('x', 45)(caja)
caja_final = translate(10, 0, 0)(caja_rotada)