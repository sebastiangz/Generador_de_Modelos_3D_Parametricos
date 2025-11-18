# 📚 Referencia Matemática: Generador 3D Funcional
# (Versión en lenguaje conceptual)

Este documento explica las ideas matemáticas detrás del proyecto, usando lenguaje simple.

---

## 1. 📐 Álgebra Lineal y Coordenadas
**(Archivos: `src/vectors.py`, `src/transforms.py`)**

Esta es la base para mover, girar y escalar objetos.

### 1.1. Vector3
Es un paquete de 3 números `(x, y, z)` que puede representar dos cosas:
1.  Un **Punto:** Una ubicación exacta en el espacio 3D.
2.  Un **Vector:** Una dirección y una longitud (como "dos pasos hacia adelante y uno arriba").

Operaciones clave:

* **Producto Punto (Dot Product):** Te dice qué tanto "apunta" un vector en la misma dirección que otro.
    * **Cómo se calcula:** Se multiplican los componentes (x con x, y con y, z con z) y se suman esos 3 resultados.

* **Producto Cruz (Cross Product):** Te da un nuevo vector que es perfectamente perpendicular (en 90 grados) a los dos vectores originales.

* **Magnitud (Magnitude):** Te dice qué tan "largo" es un vector.
    * **Cómo se calcula:** Es la raíz cuadrada de la suma de cada componente al cuadrado (`x*x + y*y + z*z`). Es básicamente el Teorema de Pitágoras en 3D.

### 1.2. Matrix4x4 y Coordenadas Homogéneas
Una matriz 4x4 es una cuadrícula de números (4 filas por 4 columnas) que actúa como una "máquina de transformación" universal.

Para que funcione, convertimos nuestros puntos 3D `(x, y, z)` en puntos 4D `(x, y, z, 1)`. Este "1" extra es un truco matemático (llamado coordenada homogénea) que permite que una sola matriz haga *todas* las transformaciones.

### 1.3. Matrices de Transformación
La fórmula es siempre: `Punto_Nuevo = Matriz_Transformacion * Punto_Original`

* **Matriz de Traslación (Mover):**
    Esta matriz le dice al punto "súmale este valor a tu x, este a tu y, y este a tu z".
    `[1, 0, 0, valor_a_mover_x]`
    `[0, 1, 0, valor_a_mover_y]`
    `[0, 0, 1, valor_a_mover_z]`
    `[0, 0, 0, 1]`

* **Matriz de Escala (Cambiar tamaño):**
    Esta matriz le dice al punto "multiplica tu x por este factor, tu y por este otro, etc."
    `[factor_x, 0, 0, 0]`
    `[0, factor_y, 0, 0]`
    `[0, 0, factor_z, 0]`
    `[0, 0, 0,        1]`

* **Matriz de Rotación (Girar):**
    Esta es la más compleja. Usa funciones trigonométricas (Seno y Coseno) para calcular la nueva posición (x, y, z) del punto después de girarlo alrededor de un eje.

### 1.4. Composición
La "magia" de las matrices es que puedes combinarlas. Si quieres "primero escalar y luego girar", simplemente multiplicas la `Matriz_Rotacion` por la `Matriz_Escala`. El resultado es una *única matriz nueva* que hace ambas cosas a la vez.

---

## 2. 🧊 Geometría Implícita (Primitivas)
**(Archivo: `src/geometry.py`)**

Este es un enfoque diferente para definir una forma. En lugar de decir "aquí están los vértices", decimos: "una forma es una regla que te dice si un punto está **dentro** o **fuera**".

Esta regla es la función `contains(punto)`.

* **Esfera:**
    * **Regla:** "Un punto está *dentro* si su distancia al centro es menor o igual al radio."

* **Caja (Box):**
    * **Regla:** "Un punto está *dentro* si su `x` está entre -ancho/2 y +ancho/2, su `y` está entre -alto/2 y +alto/2, Y su `z` está entre -profundo/2 y +profundo/2."

* **Cilindro (parado en Z):**
    * **Regla:** "Un punto está *dentro* si su distancia al eje Z es menor que el radio Y su altura (`z`) está dentro de los límites."

* **Toro (Dona):**
    * **Regla:** "Un punto está *dentro* si su distancia al 'tubo' central de la dona es menor que el radio del 'tubo'."

* **Cono:**
    * **Regla:** "Es como un cilindro, pero el radio permitido se hace más pequeño a medida que el punto está más alto."

---

## 3. 🧩 Geometría Sólida Constructiva (CSG)
**(Archivo: `src/csg.py`)**

CSG es el arte de combinar las formas implícitas usando operaciones lógicas (booleanas).

### 3.1. Operaciones Booleanas
* **Unión:** (Forma A + Forma B)
    * **Regla:** "Un punto está en la unión si está *dentro* de A **O** está *dentro* de B."

* **Intersección:** (Donde A y B se empalman)
    * **Regla:** "Un punto está en la intersección si está *dentro* de A **Y** está *dentro* de B."

* **Diferencia:** (Forma A - Forma B)
    * **Regla:** "Un punto está en la diferencia si está *dentro* de A **Y NO** está *dentro* de B."

### 3.2. Transformaciones en Sólidos CSG
¿Cómo movemos un sólido CSG si solo es una "regla"?
No movemos el sólido. Hacemos lo opuesto: movemos el punto que estamos probando.

Si queremos saber si un punto `P` está en un *sólido movido*:
1.  Movemos el punto `P` **hacia atrás** (con la matriz inversa).
2.  Probamos ese punto (movido-hacia-atrás) contra el sólido *original*.

**Regla:** `El_punto_esta_en_el_solido_movido = El_punto_movido_hacia_atras_esta_en_el_solido_original`

---

## 4. 📈 Curvas y Superficies Paramétricas
**(Archivos: `src/curves.py`, `src/surfaces.py`)**

Este es el *tercer* método. Aquí, definimos una forma con una función que, en lugar de decir "dentro/fuera", **dibuja** la forma.

Le das un número `t` (de 0 a 1) y la función te devuelve el punto exacto en la línea.

### 4.1. Curva de Bézier Cúbica
Usa 4 puntos (P0, P1, P2, P3).
* **Concepto:** Es un "promedio ponderado" de los 4 puntos.
* Cuando `t=0`, el 100% del peso está en `P0` (el inicio).
* Cuando `t=1`, el 100% del peso está en `P3` (el final).
* En medio (`t=0.5`), todos los puntos aportan algo, pero `P1` y `P2` (los puntos de control) "jalan" la curva hacia ellos.

### 4.2. B-Splines y NURBS
* **B-Spline:** Es como una Bézier, pero puedes usar *tantos puntos de control como quieras* para hacer curvas más largas y complejas.
* **NURBS:** Es la más avanzada. Es una B-Spline, pero cada punto de control tiene un **"peso"** (como un imán). Un punto con más peso "jala" la curva hacia él con más fuerza. Esto permite crear círculos y arcos perfectos.

### 4.3. Superficie de Revolución
Crea una forma 3D "torneando" una línea 2D alrededor de un eje.
1.  Defines un perfil 2D (como la silueta de una copa). Esta línea usa un parámetro `u`.
2.  Defines un segundo parámetro, `v` (de 0 a 1), para la rotación (0 = 0 grados, 1 = 360 grados).
3.  La función `S(u, v)` te da el punto 3D exacto:
    * `u` te dice qué tan "alto" estás en la silueta.
    * `v` te dice qué tanto has "girado" ese punto alrededor del eje.

---

## 5. 🕸️ Generación de Mallas (Meshing)
**(Archivo: `src/mesh.py`)**

Este archivo es el puente final: convierte las "reglas" matemáticas en un objeto 3D real (una malla de triángulos).

### 5.1. Malla desde Sólido (Marching Cubes)
Convierte una regla `contains` (CSG) en una malla.
1.  **Voxelizar:** Divide el espacio del objeto en una cuadrícula de cubos diminutos (vóxeles).
2.  **Probar:** Prueba la regla `contains` en cada esquina de cada cubo.
3.  **Dibujar:** Si una esquina está "dentro" (1) y otra está "fuera" (0), el algoritmo sabe que la superficie pasa por en medio de ellas.
4.  Dibuja los triángulos necesarios dentro de ese cubo para representar ese pedacito de superficie.

### 5.2. Malla desde Superficie (Grid Sampling)
Convierte una superficie `S(u, v)` en una malla.
1.  **Crear Rejilla:** Crea una rejilla 2D (como una hoja de cálculo) de valores `u` y `v`.
2.  **Muestrear:** Calcula el punto 3D para cada celda de la rejilla. Ahora tienes una "red de pesca" de puntos 3D.
3.  **Conectar:** Conecta los puntos. Cada 4 puntos de la red forman un cuadrado, que se divide en dos triángulos.