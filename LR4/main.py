import pygame as pg
import sys

from drawer import draw_edges, draw_help, draw_vertices
from button import button
from algorithms import Transform3D
from consts import SIZE, NAME, FIELD_RECT, FONT_SIZE, WHITE, GRAY, BLACK

def load_object(filename="object.txt"):
    vertices = []
    edges = []
    try:
        with open(filename, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
            n = int(lines[0])
            for i in range(1, n + 1):
                x, y, z = map(float, lines[i].split())
                vertices.append([x, y, z]) 
            m = int(lines[n + 1])
            for i in range(n + 2, n + 2 + m):
                a, b = map(int, lines[i].split())
                edges.append((a - 1, b - 1))
            
    except:
        print("Объект не загружен или не валидный, используется куб 2*2*2")
        vertices = [[-1,-1,-1], [1,-1,-1], [1,1,-1], [-1,1,-1],
                    [-1,-1,1], [1,-1,1], [1,1,1], [-1,1,1]]
        edges = [(0,1),(1,2),(2,3),(3,0),
                 (4,5),(5,6),(6,7),(7,4),
                 (0,4),(1,5),(2,6),(3,7)]
    return vertices, edges

def project_2d(point3d, d=5.0):
    x, y, z = point3d

    # защита от деления на 0
    if abs(z + d) < 1e-6:
        z += 1e-6

    factor = d / (z + d)
    return (x * factor, y * factor)


pg.init()
screen = pg.display.set_mode(SIZE)
pg.display.set_caption(NAME)
clock = pg.time.Clock()

trans = Transform3D()
vertices, edges = load_object()
current_vertices = [list(p) for p in vertices]  

button_clear = button((20, 20, 200, 50), "Сбросить")
button_load = button((20, 90, 200, 50), "Загрузить файл")

angle_step = 0.2
scale_step = 0.2
trans_step = 0.2
d = 5.0

run = True
while run:
    screen.fill(WHITE)
    pg.draw.rect(screen, GRAY, FIELD_RECT, 3)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False

        if button_clear.is_press(event):
            current_vertices = [list(p) for p in vertices]

        if button_load.is_press(event):
            vertices, edges = load_object()
            current_vertices = [list(p) for p in vertices]

        if event.type == pg.KEYDOWN:
            mats = []

            # перемещение
            if event.key == pg.K_LEFT:
                mats.append(trans.translate(-trans_step, 0, 0))
            elif event.key == pg.K_RIGHT:
                mats.append(trans.translate(trans_step, 0, 0))
            elif event.key == pg.K_UP:
                mats.append(trans.translate(0, trans_step, 0))
            elif event.key == pg.K_DOWN:
                mats.append(trans.translate(0, -trans_step, 0))
            elif event.key == pg.K_PAGEUP:
                mats.append(trans.translate(0, 0, trans_step))
            elif event.key == pg.K_PAGEDOWN:
                mats.append(trans.translate(0, 0, -trans_step))

            # повороты
            elif event.key == pg.K_q:
                mats.append(trans.rotate_x(angle_step))
            elif event.key == pg.K_a:
                mats.append(trans.rotate_x(-angle_step))
            elif event.key == pg.K_w:
                mats.append(trans.rotate_y(angle_step))
            elif event.key == pg.K_s:
                mats.append(trans.rotate_y(-angle_step))
            elif event.key == pg.K_e:
                mats.append(trans.rotate_z(angle_step))
            elif event.key == pg.K_d:
                mats.append(trans.rotate_z(-angle_step))

            # масштаб
            elif event.key == pg.K_PLUS or event.key == pg.K_KP_PLUS:
                mats.append(trans.scale(1 + scale_step, 1 + scale_step, 1 + scale_step))
            elif event.key == pg.K_MINUS or event.key == pg.K_KP_MINUS:
                mats.append(trans.scale(1 - scale_step, 1 - scale_step, 1 - scale_step))

            # отражения
            elif event.key == pg.K_r:
                mats.append(trans.reflect_xy())
            elif event.key == pg.K_t:
                mats.append(trans.reflect_xz())
            elif event.key == pg.K_y:
                mats.append(trans.reflect_yz())

            # перспектива
            elif event.key == pg.K_p:
                d = max(1.0, d - 0.5)
            elif event.key == pg.K_o:
                d = d + 0.5

            if mats:
                M = trans.compose(mats)
                current_vertices = trans.apply(current_vertices, M)

    proj_points = []
    for p in current_vertices:
        px, py = project_2d(p, d)

        sx = FIELD_RECT[0] + FIELD_RECT[2] // 2 + int(px * 150)
        sy = FIELD_RECT[1] + FIELD_RECT[3] // 2 - int(py * 150)

        proj_points.append((sx, sy))

    draw_edges(edges, proj_points, screen)

    draw_vertices(proj_points, screen)

    button_clear.draw(screen, False)
    button_load.draw(screen, False)

    draw_help(screen)

    pg.display.flip()
    clock.tick(60)

pg.quit()
sys.exit()