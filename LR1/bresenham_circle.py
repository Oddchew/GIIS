import pygame
def bresenham_circle_pixels(cx: int, cy: int, r: int) -> list[tuple[int, int]]:
    """Генерирует пиксели окружности."""
    pixels = []
    x, y = 0, r
    p = 3 - 2 * r
    
    while x <= y:
        # 8 симметричных точек
        points = [
            (cx + x, cy + y), (cx - x, cy + y), (cx + x, cy - y), (cx - x, cy - y),
            (cx + y, cy + x), (cx - y, cy + x), (cx + y, cy - x), (cx - y, cy - x)
        ]
        pixels.extend(points)
        
        if p < 0:
            p += 4 * x + 6
        else:
            y -= 1
            p += 4 * (x - y) + 10
        x += 1
    
    return pixels