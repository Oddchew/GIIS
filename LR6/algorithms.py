def orientation(p, q, r):
    """
    Вычисляет ориентацию тройки точек (знак векторного произведения).
    0 - коллинеарны, 1 - по часовой, 2 - против часовой.
    """
    val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
    if val == 0:
        return 0
    return 1 if val > 0 else 2


def dist_sq(a, b):
    """Квадрат расстояния"""
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


from functools import cmp_to_key


def graham_scan(points):
    """Метод обхода Грэхема"""
    if len(points) < 3:
        return points[:]

    ymin = min(range(len(points)), key=lambda i: (points[i][1], points[i][0]))
    points[0], points[ymin] = points[ymin], points[0]
    p0 = points[0]

    def polar_cmp(q, r):
        o = orientation(p0, q, r)
        if o == 0:
            return -1 if dist_sq(p0, q) < dist_sq(p0, r) else 1
        return -1 if o == 2 else 1

    points[1:] = sorted(points[1:], key=cmp_to_key(polar_cmp))

    stack = [points[0], points[1], points[2]]
    for i in range(3, len(points)):
        while len(stack) >= 2 and orientation(stack[-2], stack[-1], points[i]) != 2:
            stack.pop()
        stack.append(points[i])
    return stack


def jarvis_march(points):
    """Метод Джарвиса"""
    if len(points) < 3:
        return points[:]
    
    l = min(range(len(points)), key=lambda i: (points[i][1], points[i][0]))
    hull = []
    current = l
    while True:
        hull.append(points[current])
        next_ = (current + 1) % len(points)
        for i in range(len(points)):
            o = orientation(points[current], points[next_], points[i])
            if o == 2 or (o == 0 and dist_sq(points[current], points[i]) > dist_sq(points[current], points[next_])):
                next_ = i
        current = next_
        if current == l:
            break
    return hull


def is_convex(poly):
    """Проверка выпуклости по знакам векторных произведений"""
    n = len(poly)
    if n < 3:
        return False
    first = 0
    for i in range(n):
        o = orientation(poly[i], poly[(i + 1) % n], poly[(i + 2) % n])
        if o != 0:
            if first == 0:
                first = o
            elif first != o:
                return False
    return True


def get_internal_normals(poly):
    """Внутренние нормали"""
    n = len(poly)
    normals = []

    area = 0
    for i in range(n):
        j = (i + 1) % n
        area += poly[i][0] * poly[j][1] - poly[j][0] * poly[i][1]
    ccw = area > 0
    for i in range(n):
        p1 = poly[i]
        p2 = poly[(i + 1) % n]
        vx = p2[0] - p1[0]
        vy = p2[1] - p1[1]

        if ccw:
            nx, ny = -vy, vx
        else:
            nx, ny = vy, -vx
        length = (nx ** 2 + ny ** 2) ** 0.5
        if length == 0:
            continue
        nx = nx / length * 5  
        ny = ny / length * 5
        mid = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
        normals.append((mid, (nx, ny)))
    return normals


def segment_intersection(A, B, C, D)-> float | None:
    """
    Параметрическое нахождение точки пересечения двух отрезков
    (P(t) = P2 + (P2 - P1)*t)
    Возвращает (x, y) или None.
    """
    x1, y1 = A
    x2, y2 = B
    x3, y3 = C
    x4, y4 = D
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(den) < 1e-9:  # параллельны
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den
    if 0 <= t <= 1 and 0 <= u <= 1:
        ix = x1 + t * (x2 - x1)
        iy = y1 + t * (y2 - y1)
        return (ix, iy)
    return None


def segment_polygon_intersections(start, end, poly):
    """Все точки пересечения отрезка со сторонами полигона (округляем до сетки (целых))"""
    intersections = []
    n = len(poly)
    for i in range(n):
        p1 = poly[i]
        p2 = poly[(i + 1) % n]
        inter = segment_intersection(start, end, p1, p2)
        if inter:

            ix = round(inter[0])
            iy = round(inter[1])
            if (ix, iy) not in intersections:
                intersections.append((ix, iy))
    return intersections


def point_in_polygon(point, poly):
    """
    Принадлежность точки полигону — алгоритм «просвечивания» (ray casting).
    Стандартный метод для этой задачи
    """
    x, y = point
    n = len(poly)
    inside = False
    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside