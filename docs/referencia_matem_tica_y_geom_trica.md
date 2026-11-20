# 📐 Referencia Matemática — Modelado y Clasificación 3D

Este documento detalla las formulaciones matemáticas utilizadas en los módulos de álgebra lineal, transformaciones afines, geometría paramétrica y operaciones CSG.

---

## 1. Álgebra Lineal en Coordenadas Homogéneas

Para unificar traslaciones, rotaciones y escalados bajo una única operación de multiplicación matricial, cada vértice $\vec{v} = (x, y, z) \in \mathbb{R}^3$ se representa en el espacio proyectivo $\mathbb{P}^3$ como $\vec{v}_h = (x, y, z, 1)^T$.

### Producto Vectorial y Normales de Superficie
Dado un triángulo definido por sus vértices $(V_1, V_2, V_3)$ ordenados en sentido antihorario, el vector normal unitario $\hat{n}$ se obtiene mediante:

$$\vec{e}_1 = V_2 - V_1, \quad \vec{e}_2 = V_3 - V_1$$

$$\hat{n} = \frac{\vec{e}_1 \times \vec{e}_2}{\|\vec{e}_1 \times \vec{e}_2\|_2}$$

---

## 2. Transformaciones Afines Composables

La normalización de cualquier modelo 3D se define mediante la composición funcional de tres operadores lineales y afines:

$$T_{\text{norm}}(\vec{v}) = (S \circ R \circ T_{\text{centro}})(\vec{v})$$

1. **Traslación al Centroide del Bounding Box ($T_{\text{centro}}$):**
   $$\vec{c} = \frac{\vec{v}_{\min} + \vec{v}_{\max}}{2}, \quad T_{\text{centro}} = \begin{pmatrix} 1 & 0 & 0 & -c_x \\ 0 & 1 & 0 & -c_y \\ 0 & 0 & 1 & -c_z \\ 0 & 0 & 0 & 1 \end{pmatrix}$$

2. **Alineación del Eje Principal ($R$):**  
   Se rota la malla en múltiplos de $\frac{\pi}{2}$ alrededor de $X$ o $Y$ para garantizar que la dimensión máxima quede orientada sobre el eje $Z$:
   $$R_y\left(\frac{\pi}{2}\right) = \begin{pmatrix} 0 & 0 & 1 & 0 \\ 0 & 1 & 0 & 0 \\ -1 & 0 & 0 & 0 \\ 0 & 0 & 0 & 1 \end{pmatrix}, \quad R_x\left(-\frac{\pi}{2}\right) = \begin{pmatrix} 1 & 0 & 0 & 0 \\ 0 & 0 & 1 & 0 \\ 0 & -1 & 0 & 0 \\ 0 & 0 & 0 & 1 \end{pmatrix}$$

3. **Escalado Uniforme al Cubo Unitario ($S$):**  
   Sea $d_{\max} = \max(\Delta x, \Delta y, \Delta z)$. El factor de escala $\alpha = \frac{2}{d_{\max}}$ mapea el objeto al dominio $[-1, 1]^3$ preservando sus proporciones reales:
   $$S(\alpha) = \text{diag}(\alpha, \alpha, \alpha, 1)$$

---

## 3. Curvas y Superficies Paramétricas

### Curva de Bézier Cúbica (Empuñadura)
Para cuatro puntos de control $P_0, P_1, P_2, P_3 \in \mathbb{R}^3$ y parámetro $t \in [0, 1]$:

$$B(t) = (1 - t)^3 P_0 + 3(1 - t)^2 t P_1 + 3(1 - t) t^2 P_2 + t^3 P_3$$

### Superficie de Revolución Cilíndrica (Cañón)
Parametrizada sobre $(u, v) \in [0, 1]^2$ con radio $r$ y longitud $L$:

$$S_{\text{cañón}}(u, v) = \begin{pmatrix} r \cos(2\pi u) \\ r \sin(2\pi u) \\ (v - 0.5)L \end{pmatrix}$$

### Superficie Reglada Convergente (Hoja Punzocortante)
Con perfil de adelgazamiento parabólico $\phi(v) = \sqrt{\max(0, 1 - v^{2.2})}$ para ancho base $A$ y grosor de lomo $G$:

$$S_{\text{hoja}}(u, v) = \begin{pmatrix} \frac{G}{2} \phi(v) \sin(2\pi u) \\ \frac{A}{2} \phi(v) \cos(2\pi u) \\ (v - 0.5)L \end{pmatrix}$$

---

## 4. Geometría Constructiva de Sólidos (CSG) mediante SDF

En programación funcional pura, un sólido $\Omega \subset \mathbb{R}^3$ se representa implícitamente mediante su **Función de Distancia con Signo** $f_\Omega: \mathbb{R}^3 \to \mathbb{R}$:

$$f_\Omega(\vec{p}) \begin{cases} < 0 & \text{si } \vec{p} \in \text{int}(\Omega) \\ = 0 & \text{si } \vec{p} \in \partial\Omega \\ > 0 & \text{si } \vec{p} \notin \Omega \end{cases}$$

### Álgebra Booleana de Sólidos
Dados dos sólidos $A$ y $B$ definidos por $f_A$ y $f_B$:

* **Unión ($A \cup B$):**
  $$f_{A \cup B}(\vec{p}) = \min\big(f_A(\vec{p}),\, f_B(\vec{p})\big)$$
* **Intersección ($A \cap B$):**
  $$f_{A \cap B}(\vec{p}) = \max\big(f_A(\vec{p}),\, f_B(\vec{p})\big)$$
* **Diferencia ($A \setminus B$):**
  $$f_{A \setminus B}(\vec{p}) = \max\big(f_A(\vec{p}),\, -f_B(\vec{p})\big)$$

---

## 5. Métrica de Clasificación Híbrida

Para comparar un modelo desconocido $M_1$ contra una plantilla de referencia $M_2$, se combinan dos métricas invariantes a escala:

1. **Índice de Jaccard Volumétrico (IoU 3D):**  
   Evaluado sobre una rejilla uniforme $G \subset [-1, 1]^3$ de $N^3$ puntos:
   $$\text{IoU}(M_1, M_2) = \frac{|\{\vec{p} \in G \mid f_{M_1 \cap M_2}(\vec{p}) \le 0\}|}{|\{\vec{p} \in G \mid f_{M_1 \cup M_2}(\vec{p}) \le 0\}|}$$

2. **Similitud de Proporciones Espaciales:**  
   Sea $\vec{\rho}(M) = \frac{1}{d_{\max}}(\Delta x, \Delta y, \Delta z) \in [0, 1]^3$ el vector de relación de aspecto:
   $$S_{\text{prop}}(M_1, M_2) = 1 - \frac{\|\vec{\rho}(M_1) - \vec{\rho}(M_2)\|_2}{\sqrt{3}}$$

3. **Puntaje Final Ponderado:**
   $$\text{Score}(M_1, M_2) = 0.65 \cdot \text{IoU}(M_1, M_2) + 0.35 \cdot S_{\text{prop}}(M_1, M_2)$$