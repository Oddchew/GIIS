import math
from collections import defaultdict
from consts import FIELD_X_MAX, FIELD_Y_MAX

def get_circumcenter(t):
    a, b, c = t
    ax, ay = a
    bx, by = b
    cx, cy = c
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-9:
        return None
    ux = ((ax**2 + ay**2) * (by - cy) + (bx**2 + by**2) * (cy - ay) + (cx**2 + cy**2) * (ay - by)) / d
    uy = ((ax**2 + ay**2) * (cx - bx) + (bx**2 + by**2) * (ax - cx) + (cx**2 + cy**2) * (bx - ax)) / d
    return ux, uy

def get_raw_triangles(points):
    """Инкрементальный алгоритм триангуляции Делоне (Bowyer-Watson) - возвращает список треугольников"""
    if len(points) < 3:
        return []

    pts = sorted(set(points))
    if len(pts) < 3:
        return []

    # Определяем границы для супер-треугольника
    min_x = min(p[0] for p in pts)
    max_x = max(p[0] for p in pts)
    min_y = min(p[1] for p in pts)
    max_y = max(p[1] for p in pts)
    dx = max_x - min_x
    dy = max_y - min_y
    delta_max = max(dx, dy)
    mid_x = (min_x + max_x) / 2
    mid_y = (min_y + max_y) / 2

    # Супер-треугольник, гарантированно содержащий все точки
    super_tri = [
        (mid_x - 20 * delta_max - 100, mid_y - delta_max - 100),
        (mid_x + 20 * delta_max + 100, mid_y - delta_max - 100),
        (mid_x, mid_y + 20 * delta_max + 100)
    ]

    triangles = [tuple(super_tri)]

    def point_in_circumcircle(p, t):
        center = get_circumcenter(t)
        if center is None: return False
        ux, uy = center
        r2 = (t[0][0] - ux)**2 + (t[0][1] - uy)**2
        return (p[0] - ux)**2 + (p[1] - uy)**2 < r2 + 1e-6

    for p in pts:
        bad_triangles = [t for t in triangles if point_in_circumcircle(p, t)]
        polygon = []
        for t in bad_triangles:
            for i in range(3):
                edge = tuple(sorted((t[i], t[(i+1)%3])))
                is_shared = False
                for other in bad_triangles:
                    if other == t: continue
                    for j in range(3):
                        other_edge = tuple(sorted((other[j], other[(j+1)%3])))
                        if edge == other_edge:
                            is_shared = True
                            break
                    if is_shared: break
                if not is_shared:
                    polygon.append((t[i], t[(i+1)%3]))

        for t in bad_triangles:
            triangles.remove(t)

        for edge in polygon:
            triangles.append((edge[0], edge[1], p))

    final_triangles = []
    super_tri_set = set(super_tri)
    for t in triangles:
        if not any(pt in super_tri_set for pt in t):
            final_triangles.append(tuple(sorted(t)))

    return list(set(final_triangles))

def delaunay_triangulation(points):
    """Возвращает список уникальных обрезанных ребер триангуляции"""
    raw_triangles = get_raw_triangles(points)

    unique_edges = set()
    for t in raw_triangles:
        for i in range(3):
            edge = tuple(sorted((t[i], t[(i+1)%3])))
            unique_edges.add(edge)

    # Обрезание рёбер границами поля
    clipped_edges = []
    for p1, p2 in unique_edges:
        clipped = cohen_sutherland_clip(p1[0], p1[1], p2[0], p2[1], 0, 0, FIELD_X_MAX, FIELD_Y_MAX)
        if clipped:
            clipped_edges.append(clipped)

    return clipped_edges

def voronoi_from_delaunay(points, triangles):
    """
    Построение диаграммы Вороного.
    Для каждого внутреннего ребра триангуляции соединяем центры описанных окружностей прилегающих треугольников.
    """
    if not triangles:
        return []

    # Составим карту: ребро -> список треугольников, которым оно принадлежит
    edge_to_tris = defaultdict(list)
    for t in triangles:
        for i in range(3):
            edge = tuple(sorted((t[i], t[(i+1)%3])))
            edge_to_tris[edge].append(t)

    vor_edges = []
    for edge, tris in edge_to_tris.items():
        if len(tris) == 2:
            # Внутреннее ребро
            c1 = get_circumcenter(tris[0])
            c2 = get_circumcenter(tris[1])
            if c1 and c2:
                vor_edges.append((c1, c2))
        elif len(tris) == 1:
            # Ребро на границе (выпуклая оболочка)
            t = tris[0]
            c = get_circumcenter(t)
            if not c: continue

            p1, p2 = edge
            p3 = [p for p in t if p != p1 and p != p2][0]

            mid_x = (p1[0] + p2[0]) / 2
            mid_y = (p1[1] + p2[1]) / 2

            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]

            # Вектор перпендикуляра
            n = (-dy, dx)

            # Проверяем направление n: должно смотреть от p3
            v_mid_p3 = (p3[0] - mid_x, p3[1] - mid_y)
            dot = n[0] * v_mid_p3[0] + n[1] * v_mid_p3[1]

            if dot > 0:
                n = (-n[0], -n[1])

            # Нормализуем n для стабильности луча
            length = math.hypot(n[0], n[1])
            if length > 1e-9:
                n = (n[0] / length, n[1] / length)
                far_p = (c[0] + n[0] * 1000, c[1] + n[1] * 1000)
                vor_edges.append((c, far_p))

    # Обрезание рёбер границами поля
    clipped_vor_edges = []
    for p1, p2 in vor_edges:
        clipped = cohen_sutherland_clip(p1[0], p1[1], p2[0], p2[1], 0, 0, FIELD_X_MAX, FIELD_Y_MAX)
        if clipped:
            clipped_vor_edges.append(clipped)

    return clipped_vor_edges

# Cohen-Sutherland clipping
INSIDE = 0  # 0000
LEFT = 1    # 0001
RIGHT = 2   # 0010
BOTTOM = 4  # 0100
TOP = 8     # 1000

def compute_code(x, y, x_min, y_min, x_max, y_max):
    code = INSIDE
    if x < x_min:
        code |= LEFT
    elif x > x_max:
        code |= RIGHT
    if y < y_min:
        code |= BOTTOM
    elif y > y_max:
        code |= TOP
    return code

def cohen_sutherland_clip(x1, y1, x2, y2, x_min, y_min, x_max, y_max):
    code1 = compute_code(x1, y1, x_min, y_min, x_max, y_max)
    code2 = compute_code(x2, y2, x_min, y_min, x_max, y_max)
    accept = False

    while True:
        if code1 == 0 and code2 == 0:
            accept = True
            break
        elif (code1 & code2) != 0:
            break
        else:
            x = 0
            y = 0
            if code1 != 0:
                code_out = code1
            else:
                code_out = code2

            if code_out & TOP:
                if (y2 - y1) == 0:
                    x = x1
                else:
                    x = x1 + (x2 - x1) * (y_max - y1) / (y2 - y1)
                y = y_max
            elif code_out & BOTTOM:
                if (y2 - y1) == 0:
                    x = x1
                else:
                    x = x1 + (x2 - x1) * (y_min - y1) / (y2 - y1)
                y = y_min
            elif code_out & RIGHT:
                if (x2 - x1) == 0:
                    y = y1
                else:
                    y = y1 + (y2 - y1) * (x_max - x1) / (x2 - x1)
                x = x_max
            elif code_out & LEFT:
                if (x2 - x1) == 0:
                    y = y1
                else:
                    y = y1 + (y2 - y1) * (x_min - x1) / (x2 - x1)
                x = x_min

            if code_out == code1:
                x1 = x
                y1 = y
                code1 = compute_code(x1, y1, x_min, y_min, x_max, y_max)
            else:
                x2 = x
                y2 = y
                code2 = compute_code(x2, y2, x_min, y_min, x_max, y_max)

    if accept:
        return (int(round(x1)), int(round(y1))), (int(round(x2)), int(round(y2)))
    else:
        return None
