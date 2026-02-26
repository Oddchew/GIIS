import pygame as pg
BLACK = (0, 0, 0)

def DDA(x1: int, y1: int, x2: int, y2: int) -> list[tuple[int,int]]:
    """
    Генерирует пиксели отрезка цифровым дифференциальным анализатором.
    """
    dx = x2 - x1
    dy = y2 - y1
    
    steps = max(abs(dx),abs(dy))
    x_increment = dx / steps
    y_increment = dy / steps
    
    x = x1
    y = y1
    
    points = []
    
    for _ in range(steps):
        x += x_increment
        y += y_increment
        points.append((round(x), round(y)))
    
    return points