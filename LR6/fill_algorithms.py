from collections import deque
import math
from algorithms import point_in_polygon  

def scanline_edge_table(poly, debug=False):
    if len(poly) < 3:
        return [], []
    
    filled = []
    debug_info = ["=== Scan ET ==="] if debug else None

    edges = []
    n = len(poly)
    
    for i in range(n):
        p1 = poly[i]
        p2 = poly[(i + 1) % n]
        
        x1, y1 = float(p1[0]), float(p1[1])
        x2, y2 = float(p2[0]), float(p2[1])

        if y1 == y2:
            continue 

        if y1 > y2:
            y1, y2 = y2, y1
            x1, x2 = x2, x1

        edges.append({
            'ymin': int(y1),
            'ymax': int(y2),
            'x': x1,
            'dx': (x2 - x1) / (y2 - y1),
            'original_x': x1
        })

    if not edges:
        return [], debug_info

    edges.sort(key=lambda e: e['ymin'])

    y_min = min(e['ymin'] for e in edges)
    y_max = max(e['ymax'] for e in edges)

    for y in range(y_min, y_max):
        active = [e for e in edges if e['ymin'] <= y < e['ymax']]
        
        if not active:
            continue

        xs = []
        for e in active:
            xs.append(e['x'])
            e['x'] += e['dx']

        xs.sort()

        for i in range(0, len(xs) - 1, 2):
            x_start = xs[i]
            x_end = xs[i+1]

            ix_start = math.ceil(x_start)
            ix_end = math.floor(x_end)

            if ix_start <= ix_end:
                for x in range(ix_start, ix_end + 1):
                    filled.append((x, y))

        if debug:
            pairs = []
            for i in range(0, len(xs) - 1, 2):
                pairs.append(f"({math.ceil(xs[i])}-{math.floor(xs[i+1])})")
            debug_info.append(f"Y={y} | Intersections={xs} | Spans={pairs}")

    return filled, debug_info


def scanline_active_edge(poly, debug=False):
    """2. Алгоритм с Active Edge Table (AET)"""
    if len(poly) < 3:
        return [], []
    
    filled = []
    debug_info = ["=== Scan AET ==="] if debug else None

    edges = []
    n = len(poly)
    for i in range(n):
        p1 = poly[i]
        p2 = poly[(i + 1) % n]
        if p1[1] > p2[1]:
            p1, p2 = p2, p1
        if p1[1] != p2[1]:
            edges.append({
                'y_min': p1[1],
                'y_max': p2[1],
                'x': float(p1[0]),
                'dx': (p2[0] - p1[0]) / (p2[1] - p1[1])
            })

    if not edges:
        return [], []

    edges.sort(key=lambda e: e['y_min'])
    y = min(e['y_min'] for e in edges)
    y_max = max(e['y_max'] for e in edges)
    aet = []

    while y <= y_max:
        while edges and edges[0]['y_min'] == y:
            aet.append(edges.pop(0))
        
        aet = [e for e in aet if e['y_max'] > y]
        
        if aet:
            aet.sort(key=lambda e: e['x'])
            xs = [round(e['x']) for e in aet]
            for i in range(0, len(xs) - 1, 2):
                if i + 1 < len(xs):
                    for x in range(xs[i], xs[i + 1] + 1):
                        filled.append((x, y))
            
            if debug:
                debug_info.append(f"Y={y} | xs={xs}")

        for e in aet:
            e['x'] += e['dx']
        
        y += 1

    return filled, debug_info


def flood_fill_simple(poly, seed, debug=False):
    """3. Простая затравка (стек)"""
    if not point_in_polygon(seed, poly):
        return [], ["Точка вне полигона"]
    
    filled = set()
    stack = [seed]
    debug_info = ["=== Простая затравка ==="] if debug else None

    while stack:
        x, y = stack.pop()
        if (x, y) in filled:
            continue
        filled.add((x, y))

        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
            nx, ny = x + dx, y + dy
            if point_in_polygon((nx, ny), poly) and (nx, ny) not in filled:
                stack.append((nx, ny))

    if debug:
        debug_info.append(f"Завершено. Заполнено {len(filled)} пикселей")
    return list(filled), debug_info


def flood_fill_scanline(poly, seed, debug=False):
    """4. Построчная затравка"""
    if not point_in_polygon(seed, poly):
        return [], ["Точка вне полигона"]
    
    filled = set()
    queue = deque([seed])
    debug_info = ["=== Построчная затравка ==="] if debug else None

    while queue:
        x, y = queue.popleft()
        if (x, y) in filled:
            continue

        left = x
        while point_in_polygon((left, y), poly) and (left, y) not in filled:
            filled.add((left, y))
            left -= 1
        right = x + 1
        while point_in_polygon((right, y), poly) and (right, y) not in filled:
            filled.add((right, y))
            right += 1

        for dy in [-1, 1]:
            ny = y + dy
            for nx in range(left + 1, right):
                if point_in_polygon((nx, ny), poly) and (nx, ny) not in filled:
                    queue.append((nx, ny))
                    break

        if debug:
            debug_info.append(f"Y={y} | от {left+1} до {right-1}")

    if debug:
        debug_info.append(f"Завершено. Заполнено {len(filled)} пикселей")
    return list(filled), debug_info