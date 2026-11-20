# 🎨 Proyecto 6: Detector de Armas con Modelo 3D

## 📋 Descripción del Proyecto

Sistema funcional para la detección de armas y su representación/análisis en modelos 3D mediante álgebra lineal funcional, operaciones CSG (Constructive Solid Geometry), transformaciones composables y exportación a formatos estándar (STL, OBJ).

Universidad de Colima - Ingeniería en Computación Inteligente
Materia: Programación Funcional
Profesor: Gonzalez Zepeda Sebastian
Semestre: Agosto 2026 - Enero 2027
---

## 🎯 Objetivos

- Implementar **álgebra lineal funcional** (vectores, matrices, transformaciones) para extraer proporciones espaciales y dimensiones reales que permitan **distinguir tipos de armas** (armas cortas, armas largas, objetos punzocortantes) frente a objetos cotidianos
- Desarrollar **operaciones CSG** puras (`union`, `difference`, `intersection`) para comparar la silueta volumétrica de un objeto detectado contra plantillas 3D de referencia y calcular su grado de coincidencia
- Crear **curvas y superficies** mediante funciones paramétricas para modelar contornos característicos (cañones, empuñaduras, hojas metálicas) que faciliten la clasificación geométrica
- Aplicar **transformaciones composables** (rotación, traslación, escala) para normalizar la orientación y escala de cualquier objeto detectado antes de evaluarlo
- Generar **meshes 3D** de los objetos clasificados mediante funciones puras
- Exportar los modelos 3D identificados y etiquetados en formatos estándar (STL, OBJ)


## 📂 Estructura del Proyecto

```text
Generador_de_Modelos_3D_Parametricos/
├── 3D_assets/                    # Modelos 3D de referencia por categoría (.stl)
│   ├── armas_corta.stl           # Plantilla de arma corta
│   ├── armas_largas.stl          # Plantilla de arma larga
│   ├── Misil.stl                 # Plantilla de proyectil/misil
│   └── punzocortantes.stl        # Plantilla de objeto punzocortante
├── input_analizar/               # Carpeta de entrada para el modelo 3D a evaluar
│   └── objeto_desconocido.stl    # Archivo de prueba sin clasificar
├── output_clasificados/          # Salida con mallas normalizadas y etiquetadas (.stl / .obj)
├── src/                          # Código fuente bajo el paradigma de Programación Funcional
│   ├── algebra_lineal.py         # Estructuras inmutables y operaciones vectoriales/matriciales 4x4
│   ├── clasificador.py           # Evaluación de similitud espacial (Bounding Box) y volumétrica (CSG)
│   ├── csg.py                    # Operaciones booleanas 3D puras (union, intersection, difference) con SDF
│   ├── geometria_parametrica.py  # Curvas de Bézier y superficies paramétricas (cañones, empuñaduras, hojas)
│   ├── io_meshes.py              # Lectura pura de STL (ASCII/binario) y exportación a STL y OBJ
│   ├── main.py                   # Orquestador y pipeline funcional de ejecución
│   └── transformaciones.py       # Composición de funciones (compose) y normalización de orientación/escala
├── .gitignore                    # Exclusión de archivos temporales (__pycache__, etc.)
├── README.md                     # Documentación general del proyecto
└── requirements.txt              # Dependencias del entorno (librería estándar de Python)

## 📚 Meterial 

- **Repositorio de Modelos 3D de Referencia (Creality Cloud)**: https://www.crealitycloud.com/pt *(Fuente utilizada para obtener las mallas 3D base en formato STL/OBJ de armas cortas, largas y objetos de comparación)*

