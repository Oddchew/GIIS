import math
from collections import defaultdict

def delaunay_triangulation(points):
    """Инкрементальный алгоритм триангуляции Делоне"""
    if len(points) < 3:
        return []

    pts = sorted(set(points))  # удаляем дубликаты и сортируем
    if len(pts) < 3:
        return []

    # Супер-треугольник
    min_x = min(p[0] for p in pts) - 10
    max_x = max(p[0] for p in pts) + 10
    min_y = min(p[1] for p in pts) - 10
    max_y = max(p[1] for p in pts) + 10

    super_tri = [
        (min_x - 100, min_y - 100),
        (max_x + 100, min_y - 100),
        (min_x + (max_x - min_x) // 2, max_y + 200)
    ]

    triangles = [super_tri[:]]

    def circumcircle(t):
        a, b, c = t
        ax, ay = a; bx, by = b; cx, cy = c
        d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
        if abs(d) < 1e-6:
            return (0, 0, float('inf'))
        ux = ((ax**2 + ay**2) * (by - cy) + (bx**2 + by**2) * (cy - ay) + (cx**2 + cy**2) * (ay - by)) / d
        uy = ((ax**2 + ay**2) * (cx - bx) + (bx**2 + by**2) * (ax - cx) + (cx**2 + cy**2) * (bx - ax)) / d
        r2 = (ax - ux)**2 + (ay - uy)**2
        return ux, uy, r2

    def point_in_circle(p, t):
        cx, cy, r2 = circumcircle(t)
        return (p[0] - cx)**2 + (p[1] - cy)**2 < r2 + 1e-4

    for p in pts:
        bad = [t for t in triangles if point_in_circle(p, t)]

        polygon = []
        edge_count = defaultdict(int)
        for t in bad:
            edges = [(t[0], t[1]), (t[1], t[2]), (t[2], t[0])]
            for e in edges:
                edge_count[tuple(sorted(e))] += 1

        for e, cnt in edge_count.items():
            if cnt == 1:
                polygon.append(e)

        for t in bad:
            if t in triangles:
                triangles.remove(t)

        for e in polygon:
            triangles.append([e[0], e[1], p])

    # Удаляем треугольники с вершинами супер-треугольника
    final = []
    for t in triangles:
        if all(pt not in super_tri for pt in t):
            final.append(tuple(sorted(t)))

    return list(set(final))  # убираем возможные дубли



def voronoi_from_delaunay(points, triangles):
    """Построение рёбер диаграммы Вороного через перпендикулярные биссектрисы"""
    if not triangles:
        return []

    edges = set()
    for t in triangles:
        for i in range(3):
            a = t[i]
            b = t[(i + 1) % 3]
            if a > b:
                a, b = b, a
            edges.add((a, b))

    vor_edges = []
    for a, b in edges:
        mx = (a[0] + b[0]) / 2.0
        my = (a[1] + b[1]) / 2.0
        dx = b[1] - a[1]   # перпендикуляр
        dy = a[0] - b[0]
        length = math.hypot(dx, dy)
        if length < 1e-6:
            continue
        dx /= length * 2
        dy /= length * 2

        # Длинные отрезки для визуализации
        p1 = (int(mx + dx * 1000), int(my + dy * 1000))
        p2 = (int(mx - dx * 1000), int(my - dy * 1000))
        vor_edges.append((p1, p2))

    return vor_edges