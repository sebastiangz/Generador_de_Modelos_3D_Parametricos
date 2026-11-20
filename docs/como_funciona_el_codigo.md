# Identificador 3D de Armas (`v1.0`)

**Autor:** Christian Alberto Gomez Cardona  
**Lenguaje:** Python puro (sin dependencias externas)

## Descripción general

Este programa analiza modelos tridimensionales en formatos **`.STL`** (binario o ASCII) y **`.OBJ`** para extraer su geometría básica y clasificar el objeto dentro de cuatro categorías predefinidas:

- Pistola Táctica (Tipo M1911)
- Espada Ornamental / Fantasía
- Misil / Proyectil Guiado
- Rifle Pesado / Lanzagranadas Sci-Fi

## ¿Cómo funciona?

1. **Lectura de mallas 3D (`_load_mesh_vertices`)**
   - En archivos `.OBJ` lee líneas de vértices (`v`) y caras (`f`).
   - En archivos `.STL` detecta si es binario (validando tamaño con `struct.unpack`) y extrae los tres vértices de cada triángulo; si no, lo lee como texto buscando líneas `vertex`.

2. **Alineación por ejes principales con PCA y Jacobi (`_align_vertices_pca` / `_jacobi_eigen_3x3`)**
   - Calcula el centroide de la nube de puntos y construye la matriz de covarianza de $3 \times 3$.
   - Obtiene autovalores y autovectores mediante rotaciones de Jacobi y ordena de mayor a menor para alinear el modelo según sus ejes principales (largo, ancho y grosor), haciendo el análisis independiente de la rotación original.

3. **Extracción de métricas y clasificación (`identify_weapon_3d`)**
   - Calcula dimensiones sobre los ejes alineados, razones de *elongación* y *aplanamiento*, *asimetría bilateral* y la variación del ancho a lo largo de cuatro cuartiles del eje principal.
   - Asigna puntajes por reglas a cada categoría, elige la de mayor puntaje y calcula un porcentaje de confianza acotado entre `55.0%` y `99.0%`.

4. **Interfaz por consola y exportación a CSV (`main`, `print_identification_report`, `export_csv_report`)**
   - Permite analizar un archivo individual, escanear carpetas completas con `os.walk` y guardar el historial de la sesión en un archivo `.csv` con marca de tiempo.

## ¿Tiene programación funcional?

Tiene **algunos elementos de estilo funcional**, pero **no es completa mente funcional** 

- **Rasgos funcionales presentes:** división en funciones enfocadas, uso de expresiones generadoras (`sum(...)`), funciones clave como `max(..., key=scores.get)` o `sort(key=lambda ...)`, y construcción de nuevas estructuras en funciones como `_align_vertices_pca` e `identify_weapon_3d`.
- **Por qué es principalmente imperativo:** usa bucles (`while`, `for`), variables acumuladoras y estructuras mutables (`session_history`, diccionarios de puntajes), además de realizar operaciones de entrada/salida (`input()`, `print()`, lectura y escritura de archivos).

## Notas y limitaciones

- La **confianza** reportada corresponde a un puntaje heurístico basado en reglas y umbrales geométricos, no a una probabilidad estadística entrenada.
- Si se pasa una malla vacía (0 vértices) directamente a `_align_vertices_pca`, se produciría una división entre cero; conviene validar la cantidad de vértices antes de calcular el promedio.