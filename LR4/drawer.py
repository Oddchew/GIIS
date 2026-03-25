import pygame as pg
from consts import FONT_SIZE, INSIDE, LEFT, RIGHT, SIZE, TOP, BOTTOM, FIELD_RECT, BLACK, RED


def inside_rect(x, y, rect):
    rx, ry, rw, rh = rect
    return rx <= x <= rx + rw and ry <= y <= ry + rh

def compute_code(x, y, rect):
    rx, ry, rw, rh = rect
    code = INSIDE

    if x < rx:
        code |= LEFT
    elif x > rx + rw:
        code |= RIGHT

    if y < ry:
        code |= TOP
    elif y > ry + rh:
        code |= BOTTOM

    return code


def clip_line(x1, y1, x2, y2, rect):
    rx, ry, rw, rh = rect

    code1 = compute_code(x1, y1, rect)
    code2 = compute_code(x2, y2, rect)

    while True:
        if code1 == 0 and code2 == 0:
            return x1, y1, x2, y2

        if code1 & code2:
            return None

        code_out = code1 if code1 != 0 else code2

        if code_out & TOP:
            x = x1 + (x2 - x1) * (ry - y1) / (y2 - y1)
            y = ry
        elif code_out & BOTTOM:
            x = x1 + (x2 - x1) * (ry + rh - y1) / (y2 - y1)
            y = ry + rh
        elif code_out & RIGHT:
            y = y1 + (y2 - y1) * (rx + rw - x1) / (x2 - x1)
            x = rx + rw
        elif code_out & LEFT:
            y = y1 + (y2 - y1) * (rx - x1) / (x2 - x1)
            x = rx

        if code_out == code1:
            x1, y1 = x, y
            code1 = compute_code(x1, y1, rect)
        else:
            x2, y2 = x, y
            code2 = compute_code(x2, y2, rect)

def draw_edges(edges, proj_points, screen):
    for a, b in edges:
        x1, y1 = proj_points[a]
        x2, y2 = proj_points[b]

        clipped = clip_line(x1, y1, x2, y2, FIELD_RECT)

        if clipped:
            cx1, cy1, cx2, cy2 = clipped
            pg.draw.line(screen, BLACK, (cx1, cy1), (cx2, cy2), 2)

def draw_vertices(proj_points, screen):
    for x, y in proj_points:
        if inside_rect(x, y, FIELD_RECT):
            pg.draw.circle(screen, RED, (x, y), 4)

def draw_help(screen):
    font = pg.font.Font(None, FONT_SIZE)
    txt = font.render(
        "←→↑↓ PgUp/PgDn - перемещение | QWASD - поворот | +/- - масштаб | R/T/Y - отражение | P/O - перспектива",
        True, BLACK)
    screen.blit(txt, (20, SIZE[1] - 30))