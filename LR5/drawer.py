import pygame as pg
from bresenham import bresenham_pixels
from consts import BLACK, GREEN, RED, SCALE, FIELD_RECT

def draw_line(points, screen, color=BLACK):
    for point in points:
        if len(point) == 3:
            x, y, brightness = point
            alpha = int(255 * brightness)
            s = pg.Surface((SCALE, SCALE), pg.SRCALPHA)
            s.fill((0, 0, 0, alpha))
            screen.blit(s, (FIELD_RECT[0] + SCALE * x, FIELD_RECT[1] + SCALE * y))
        else:
            x, y = point
            rect = pg.Rect((FIELD_RECT[0] + SCALE * x, FIELD_RECT[1] + SCALE * y, SCALE, SCALE))
            pg.draw.rect(screen, color, rect)

def draw_pts(lines, screen):
    for pts in lines:
        draw_line(pts, screen)

def draw_polygons(polygons, screen):
    for poly in polygons:
        n = len(poly)
        for i in range(n):
            p1 = poly[i]
            p2 = poly[(i + 1) % n]
            side = bresenham_pixels(p1[0], p1[1], p2[0], p2[1])
            draw_line(side, screen)

def draw_current_polygon(current_polygon, screen):
    if current_polygon:
        for i in range(len(current_polygon) - 1):
            p1 = current_polygon[i]
            p2 = current_polygon[i + 1]
            side = bresenham_pixels(p1[0], p1[1], p2[0], p2[1])
            draw_line(side, screen, (100, 100, 255))

def draw_normals(normals, screen):
    for mid, (nx, ny) in normals:
        mx, my = int(mid[0]), int(mid[1])
        ex, ey = int(mid[0] + nx), int(mid[1] + ny)
        normal_line = bresenham_pixels(mx, my, ex, ey)
        draw_line(normal_line, screen, (0, 200, 0))

def draw_intersections(intersections, screen):
    for inter in intersections:
        rx = FIELD_RECT[0] + SCALE * inter[0]
        ry = FIELD_RECT[1] + SCALE * inter[1]
        pg.draw.rect(screen, RED, (rx, ry, SCALE, SCALE), 2)

def draw_point_check(last_point_check, point_check_inside, screen):
    if last_point_check:
        px, py = last_point_check
        color = GREEN if point_check_inside else RED
        rx = FIELD_RECT[0] + SCALE * px
        ry = FIELD_RECT[1] + SCALE * py
        pg.draw.rect(screen, color, (rx, ry, SCALE, SCALE), 3)