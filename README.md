# 🎨 Proyecto 6: Detector de Armas con Modelo 3D

## 📋 Descripción del Proyecto

Sistema funcional para la detección de armas y su representación/análisis en modelos 3D mediante álgebra lineal funcional, operaciones CSG (Constructive Solid Geometry), transformaciones composables y exportación a formatos estándar (STL, OBJ).

Universidad de Colima - Ingeniería en Computación Inteligente
Materia: Programación Funcional
Profesor: Gonzalez Zepeda Sebastian
Semestre: Agosto 2025 - Enero 2026
---

## 🎯 Objetivos

- Implementar **álgebra lineal funcional** (vectores, matrices, transformaciones) para extraer proporciones espaciales y dimensiones reales que permitan **distinguir tipos de armas** (armas cortas, armas largas, objetos punzocortantes) frente a objetos cotidianos
- Desarrollar **operaciones CSG** puras (`union`, `difference`, `intersection`) para comparar la silueta volumétrica de un objeto detectado contra plantillas 3D de referencia y calcular su grado de coincidencia
- Crear **curvas y superficies** mediante funciones paramétricas para modelar contornos característicos (cañones, empuñaduras, hojas metálicas) que faciliten la clasificación geométrica
- Aplicar **transformaciones composables** (rotación, traslación, escala) para normalizar la orientación y escala de cualquier objeto detectado antes de evaluarlo
- Generar **meshes 3D** de los objetos clasificados mediante funciones puras
- Exportar los modelos 3D identificados y etiquetados en formatos estándar (STL, OBJ)


## 📂 Estructura del Proyecto




## 📚 Meterial 

- **Repositorio de Modelos 3D de Referencia (Creality Cloud)**: https://www.crealitycloud.com/pt *(Fuente utilizada para obtener las mallas 3D base en formato STL/OBJ de armas cortas, largas y objetos de comparación)*

