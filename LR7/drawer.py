import pygame as pg
from consts import FIELD_RECT, SCALE, BLUE, RED
from bresenham import bresenham_pixels

def draw_line(points, screen, color):
    for x, y in points:
        rect = pg.Rect(FIELD_RECT[0] + SCALE * x,
                       FIELD_RECT[1] + SCALE * y,
                       SCALE, SCALE)
        pg.draw.rect(screen, color, rect)

def draw_points(points, screen):
    for px, py in points:
        cx = FIELD_RECT[0] + SCALE * px + SCALE // 2
        cy = FIELD_RECT[1] + SCALE * py + SCALE // 2
        pg.draw.circle(screen, (0, 0, 0), (cx, cy), SCALE // 2 + 1)

def draw_delaunay(edges, screen):
    for p1, p2 in edges:
        line = bresenham_pixels(p1[0], p1[1], p2[0], p2[1])
        draw_line(line, screen, BLUE)

def draw_voronoi(voronoi_edges, screen):
    for p1, p2 in voronoi_edges:
        line = bresenham_pixels(p1[0], p1[1], p2[0], p2[1])
        draw_line(line, screen, RED)