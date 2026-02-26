from typing import List, Tuple

def bresenham_pixels(x0: int, y0: int, x1: int, y1: int) -> list[tuple[int, int]]:
    """
    Генерирует пиксели отрезка по Брезенхему.
    """
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    pixels = [(x, y)]
    
    if dx > dy:
        err = dx / 2.0
        while x != x1:
            e2 = err
            x += sx
            err += dy
            if e2 > 0:
                y += sy
                err -= dx
            pixels.append((x, y))
    else:
        err = dy / 2.0
        while y != y1:
            e2 = err
            y += sy
            err += dx
            if e2 > 0:
                x += sx
                err -= dy
            pixels.append((x, y))
    
    return pixels
