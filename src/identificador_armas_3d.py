import os
import sys
import csv
import time
import math
import struct
from datetime import datetime


# ==============================================================================
# 📐 ÁLGEBRA 3D: ALINEACIÓN AUTOMÁTICA POR EJES PRINCIPALES (PCA / JACOBI)
# ==============================================================================

def _jacobi_eigen_3x3(cov: list[list[float]]) -> list[tuple[float, tuple[float, float, float]]]:
    """
    Calcula autovalores y autovectores de una matriz de covarianza 3x3
    mediante rotaciones de Jacobi (Python puro, sin librerías externas).
    """
    a = [row[:] for row in cov]
    v = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]

    for _ in range(30):
        p, q = 0, 1
        max_val = abs(a[0][1])
        for i, j in ((0, 2), (1, 2)):
            if abs(a[i][j]) > max_val:
                max_val = abs(a[i][j])
                p, q = i, j

        if max_val < 1e-12:
            break

        app, aqq, apq = a[p][p], a[q][q], a[p][q]
        tau = (aqq - app) / (2.0 * apq)
        if tau >= 0:
            t = 1.0 / (tau + math.sqrt(1.0 + tau * tau))
        else:
            t = -1.0 / (-tau + math.sqrt(1.0 + tau * tau))

        c = 1.0 / math.sqrt(1.0 + t * t)
        s = t * c

        a[p][p] = app - t * apq
        a[q][q] = aqq + t * apq
        a[p][q] = a[q][p] = 0.0

        for r in range(3):
            if r != p and r != q:
                arp, arq = a[r][p], a[r][q]
                a[r][p] = a[p][r] = c * arp - s * arq
                a[r][q] = a[q][r] = s * arp + c * arq

        for r in range(3):
            vrp, vrq = v[r][p], v[r][q]
            v[r][p] = c * vrp - s * vrq
            v[r][q] = s * vrp + c * vrq

    eigenpairs = [(a[i][i], (v[0][i], v[1][i], v[2][i])) for i in range(3)]
    eigenpairs.sort(key=lambda item: item[0], reverse=True)
    return eigenpairs


def _align_vertices_pca(vertices: list[tuple[float, float, float]]) -> list[tuple[float, float, float]]:
    """
    Reorienta la nube de vértices 3D hacia sus ejes naturales (Largo, Ancho, Grosor)
    para que la identificación sea invariante a la rotación del modelo.
    """
    n = len(vertices)
    cx = sum(v[0] for v in vertices) / n
    cy = sum(v[1] for v in vertices) / n
    cz = sum(v[2] for v in vertices) / n

    cxx = cxy = cxz = cyy = cyz = czz = 0.0
    for x, y, z in vertices:
        dx, dy, dz = x - cx, y - cy, z - cz
        cxx += dx * dx
        cxy += dx * dy
        cxz += dx * dz
        cyy += dy * dy
        cyz += dy * dz
        czz += dz * dz

    cov = [
        [cxx / n, cxy / n, cxz / n],
        [cxy / n, cyy / n, cyz / n],
        [cxz / n, cyz / n, czz / n],
    ]

    eigenpairs = _jacobi_eigen_3x3(cov)
    e1, e2, e3 = eigenpairs[0][1], eigenpairs[1][1], eigenpairs[2][1]

    aligned = []
    for x, y, z in vertices:
        dx, dy, dz = x - cx, y - cy, z - cz
        u1 = dx * e1[0] + dy * e1[1] + dz * e1[2]
        u2 = dx * e2[0] + dy * e2[1] + dz * e2[2]
        u3 = dx * e3[0] + dy * e3[1] + dz * e3[2]
        aligned.append((u1, u2, u3))

    return aligned


# ==============================================================================
# 🔍 LECTOR DE MALLAS 3D (.STL / .OBJ) Y MOTOR DE IDENTIFICACIÓN
# ==============================================================================

def _load_mesh_vertices(file_path: str) -> tuple[list[tuple[float, float, float]], int]:
    """
    Extrae vértices y conteo de caras/triángulos desde archivos .STL (Binario/ASCII)
    o .OBJ sin dependencias externas.
    """
    ext = os.path.splitext(file_path)[1].lower()
    vertices = []

    if ext == '.obj':
        faces = 0
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                parts = line.strip().split()
                if not parts:
                    continue
                if parts[0] == 'v' and len(parts) >= 4:
                    vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
                elif parts[0] == 'f':
                    faces += 1
        return vertices, faces

    if ext == '.stl':
        with open(file_path, 'rb') as f:
            data = f.read()

        if len(data) >= 84:
            num_triangles = struct.unpack('<I', data[80:84])[0]
            if len(data) == 84 + num_triangles * 50:
                offset = 84
                for _ in range(num_triangles):
                    v_data = struct.unpack('<9f', data[offset + 12 : offset + 48])
                    vertices.append((v_data[0], v_data[1], v_data[2]))
                    vertices.append((v_data[3], v_data[4], v_data[5]))
                    vertices.append((v_data[6], v_data[7], v_data[8]))
                    offset += 50
                return vertices, num_triangles

        text = data.decode('utf-8', errors='ignore')
        for line in text.splitlines():
            parts = line.strip().split()
            if len(parts) == 4 and parts[0].lower() == 'vertex':
                vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
        return vertices, len(vertices) // 3

    raise ValueError(f"Formato no soportado ({ext}). Usa archivos .STL o .OBJ.")


def identify_weapon_3d(mesh_path: str) -> dict:
    """
    Analiza la geometría tridimensional de un modelo y clasifica el tipo de arma:
      - Pistola Táctica (Tipo M1911)
      - Espada Ornamental / Fantasía
      - Misil / Proyectil Guiado
      - Rifle Pesado / Lanzagranadas Sci-Fi
    """
    raw_vertices, face_count = _load_mesh_vertices(mesh_path)
    if len(raw_vertices) < 4:
        raise ValueError("La malla 3D no contiene suficientes vértices válidos.")

    pts = _align_vertices_pca(raw_vertices)

    u1s = [p[0] for p in pts]
    u2s = [p[1] for p in pts]
    u3s = [p[2] for p in pts]

    min1, max1 = min(u1s), max(u1s)
    min2, max2 = min(u2s), max(u2s)
    min3, max3 = min(u3s), max(u3s)

    length = max(max1 - min1, 1e-5)    # Eje principal (Largo)
    width = max(max2 - min2, 1e-5)     # Eje secundario (Alto / Ancho)
    thickness = max(max3 - min3, 1e-5) # Eje terciario (Grosor)

    elongation = length / width
    flatness = width / thickness
    bilateral_asymmetry = abs(max2 + min2) / width

    # Análisis transversal por cuartiles a lo largo del eje principal
    quartiles = [[], [], [], []]
    for u1, u2, _ in pts:
        t = (u1 - min1) / length
        idx = min(3, int(t * 4))
        quartiles[idx].append(u2)

    q_spans = [(max(q) - min(q)) if q else 0.0 for q in quartiles]
    end_a, end_b = q_spans[0], q_spans[3]
    mid_avg = (q_spans[1] + q_spans[2]) / 2.0

    end_ratio = max(end_a, end_b) / max(min(end_a, end_b), 1e-5)
    taper_ratio = min(end_a, end_b) / max(mid_avg, 1e-5)

    scores = {
        "Pistola Táctica (Tipo M1911)": 0.0,
        "Espada Ornamental / Fantasía": 0.0,
        "Misil / Proyectil Guiado": 0.0,
        "Rifle Pesado / Lanzagranadas Sci-Fi": 0.0,
    }

    # 1. Pistola Táctica (Silueta en L, perfil delgado, empuñadura concentrada en un extremo)
    if 1.1 <= elongation <= 2.3:
        scores["Pistola Táctica (Tipo M1911)"] += 35.0
    if flatness >= 2.2:
        scores["Pistola Táctica (Tipo M1911)"] += 25.0
    if end_ratio >= 1.75:
        scores["Pistola Táctica (Tipo M1911)"] += 25.0
    if bilateral_asymmetry >= 0.15:
        scores["Pistola Táctica (Tipo M1911)"] += 15.0

    # 2. Espada Ornamental (Alta elongación, hoja plana y simetría bilateral)
    if elongation >= 3.6:
        scores["Espada Ornamental / Fantasía"] += 40.0
    elif elongation >= 2.8:
        scores["Espada Ornamental / Fantasía"] += 20.0
    if flatness >= 2.1:
        scores["Espada Ornamental / Fantasía"] += 25.0
    if bilateral_asymmetry < 0.14:
        scores["Espada Ornamental / Fantasía"] += 25.0
    if taper_ratio < 0.65:
        scores["Espada Ornamental / Fantasía"] += 10.0

    # 3. Misil / Proyectil Guiado (Sección cilíndrica/radial + punta cónica y aletas)
    if flatness <= 1.48:
        scores["Misil / Proyectil Guiado"] += 45.0
    elif flatness <= 1.75:
        scores["Misil / Proyectil Guiado"] += 20.0
    if elongation >= 2.4:
        scores["Misil / Proyectil Guiado"] += 25.0
    if bilateral_asymmetry < 0.16:
        scores["Misil / Proyectil Guiado"] += 15.0
    if taper_ratio < 0.65:
        scores["Misil / Proyectil Guiado"] += 15.0

    # 4. Rifle Pesado / Lanzagranadas Sci-Fi (Cuerpo alargado con mira, lanzagranadas y agarres)
    if 1.9 <= elongation <= 3.7:
        scores["Rifle Pesado / Lanzagranadas Sci-Fi"] += 35.0
    if 1.45 < flatness < 2.5:
        scores["Rifle Pesado / Lanzagranadas Sci-Fi"] += 25.0
    if bilateral_asymmetry >= 0.14:
        scores["Rifle Pesado / Lanzagranadas Sci-Fi"] += 20.0
    if mid_avg / width >= 0.65:
        scores["Rifle Pesado / Lanzagranadas Sci-Fi"] += 20.0

    best_weapon = max(scores, key=scores.get)
    confidence = min(99.0, max(55.0, scores[best_weapon]))

    categories = {
        "Pistola Táctica (Tipo M1911)": "Arma Corta / Secundaria",
        "Espada Ornamental / Fantasía": "Cuerpo a Cuerpo / Corte",
        "Misil / Proyectil Guiado": "Explosivo / Munición Aérea",
        "Rifle Pesado / Lanzagranadas Sci-Fi": "Arma Larga / Asalto Pesado",
    }

    return {
        "archivo": os.path.basename(mesh_path),
        "ruta": mesh_path,
        "arma_identificada": best_weapon,
        "categoria": categories[best_weapon],
        "confianza": round(confidence, 1),
        "caras": face_count,
        "dimensiones_pca": (round(length, 2), round(width, 2), round(thickness, 2)),
        "elongacion": round(elongation, 2),
        "aplanamiento": round(flatness, 2),
        "asimetria": round(bilateral_asymmetry, 3),
    }


# ==============================================================================
# 🖥️ INTERFAZ DE USUARIO (CLI) - IDENTIFICADOR 3D DE ARMAS
# ==============================================================================

def print_identification_report(report: dict):
    print("\n   " + "═" * 64)
    print(f"   🎯 RESULTADO DE IDENTIFICACIÓN 3D : {report['archivo']}")
    print("   " + "═" * 64)
    print(f"   • Arma Identificada  : {report['arma_identificada']}")
    print(f"   • Categoría          : {report['categoria']}")
    print(f"   • Confianza          : {report['confianza']}%")
    print(f"   • Dimensiones PCA    : {report['dimensiones_pca'][0]} x {report['dimensiones_pca'][1]} x {report['dimensiones_pca'][2]}")
    print(f"   • Métricas Geométricas: Elong={report['elongacion']} | Aplan={report['aplanamiento']} | Asim={report['asimetria']}")
    print(f"   • Polígonos / Caras  : {report['caras']}")
    print("   " + "═" * 64)


def export_csv_report(results: list[dict], output_path: str):
    if not results:
        print("   ⚠️ No hay análisis registrados en esta sesión para exportar.")
        return

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            "Archivo", "Arma_Identificada", "Categoria", "Confianza_%",
            "Largo_PCA", "Ancho_PCA", "Grosor_PCA",
            "Elongacion", "Aplanamiento", "Asimetria", "Caras"
        ])
        for r in results:
            writer.writerow([
                r["archivo"], r["arma_identificada"], r["categoria"], r["confianza"],
                r["dimensiones_pca"][0], r["dimensiones_pca"][1], r["dimensiones_pca"][2],
                r["elongacion"], r["aplanamiento"], r["asimetria"], r["caras"]
            ])
    print(f"\n   ✅ Reporte exportado correctamente en: {output_path}")


def main():
    print("\n" + "█" * 68)
    print("   🎯  IDENTIFICADOR 3D DE ARMAS  v1.0")
    print("   Sistema de Clasificación Morfológica de Modelos 3D (.STL / .OBJ)")
    print("█" * 68)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    session_history: list[dict] = []

    while True:
        print("\n   📂 MENÚ DEL IDENTIFICADOR:")
        print("   1. 🔍 Identificar un modelo 3D individual (.STL / .OBJ)")
        print("   2. 📁 Escanear carpeta del repositorio completa (Análisis en lote)")
        print("   3. 📊 Exportar resultados de la sesión a CSV (Reporte para entrega)")
        print("   4. 🚪 Salir")

        choice = input("\n   Selecciona una opción (1-4): ").strip()

        if choice == '4':
            print("\n   💾 Cerrando Identificador 3D de Armas...")
            break

        if choice == '1':
            target = input("\n   Ingresa la ruta del archivo 3D (.stl o .obj): ").strip().strip('"').strip("'")
            if not os.path.exists(target):
                candidate = os.path.join(base_dir, target)
                if os.path.exists(candidate):
                    target = candidate
                else:
                    print(f"   ❌ No se encontró el archivo: {target}")
                    continue

            try:
                t0 = time.time()
                report = identify_weapon_3d(target)
                elapsed = time.time() - t0
                session_history.append(report)
                print_identification_report(report)
                print(f"   ⏱️ Tiempo de análisis: {elapsed:.3f}s")
            except Exception as e:
                print(f"   ❌ Error analizando el modelo 3D: {e}")

        elif choice == '2':
            folder = input(f"\n   Ruta de la carpeta del repositorio [Enter para '{base_dir}']: ").strip().strip('"').strip("'")
            if not folder:
                folder = base_dir
            if not os.path.isdir(folder):
                print(f"   ❌ Carpeta no válida: {folder}")
                continue

            valid_exts = ('.stl', '.obj')
            mesh_files = [
                os.path.join(root, f)
                for root, _, files in os.walk(folder)
                for f in files if f.lower().endswith(valid_exts)
            ]

            if not mesh_files:
                print("   ⚠️ No se encontraron modelos 3D (.stl o .obj) en esa carpeta.")
                continue

            print(f"\n   🔎 Escaneando {len(mesh_files)} modelos 3D en el repositorio...\n")
            for path in sorted(mesh_files):
                try:
                    report = identify_weapon_3d(path)
                    session_history.append(report)
                    print_identification_report(report)
                except Exception as e:
                    print(f"   ⚠️ Error en {os.path.basename(path)}: {e}")

        elif choice == '3':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            out_csv = os.path.join(base_dir, f"reporte_identificacion_armas_{timestamp}.csv")
            export_csv_report(session_history, out_csv)


if __name__ == '__main__':
    main()