import pygame as pg
from consts import *
from button import button
from algorithms import delaunay_triangulation, voronoi_from_delaunay, get_raw_triangles
from bresenham import  bresenham_pixels
from drawer import draw_points, draw_delaunay, draw_voronoi

pg.init()
screen = pg.display.set_mode(SIZE)
pg.display.set_caption(NAME)
clock = pg.time.Clock()

# Кнопки
btn_clear = button((10, 50, 250, 50), "Очистить")
btn_delaunay = button((10, 120, 250, 50), "Триангуляция Делоне")
btn_voronoi = button((10, 190, 250, 50), "Диаграмма Вороного")

field = pg.Rect(FIELD_RECT)

points: list[tuple[int, int]] = []
triangles = []
voronoi_edges = []
mode = "Delaunay"
result_text = ""

run = True
while run:
    screen.fill(WHITE)
    pg.draw.rect(screen, WHITE, field)
    pg.draw.rect(screen, BLACK, field, 3)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False

        if btn_clear.is_press(event):
            points.clear()
            triangles.clear()
            voronoi_edges.clear()
            result_text = ""

        if btn_delaunay.is_press(event):
            mode = "Delaunay"
            if len(points) >= 3:
                triangles = delaunay_triangulation(points)
                # Передаем оригинальные точки для Вороного, если нужно, или используем triangles
                # Но triangles теперь содержит рёбра.
                # Нам нужно пересчитать triangles без обрезки для voronoi_from_delaunay или изменить voronoi_from_delaunay
                raw_triangles = get_raw_triangles(points)
                voronoi_edges = voronoi_from_delaunay(points, raw_triangles)
                result_text = f"Триангуляция Делоне: {len(triangles)} треугольников"

        if btn_voronoi.is_press(event):
            mode = "Voronoi"
            if len(points) >= 3:
                triangles = delaunay_triangulation(points)
                raw_triangles = get_raw_triangles(points)
                voronoi_edges = voronoi_from_delaunay(points, raw_triangles)
                result_text = "Диаграмма Вороного построена"

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if field.collidepoint(event.pos):
                x = int((event.pos[0] - FIELD_RECT[0]) / SCALE)
                y = int((event.pos[1] - FIELD_RECT[1]) / SCALE)
                if (x, y) not in points:
                    points.append((x, y))
                    if len(points) >= 3:
                        triangles = delaunay_triangulation(points)
                        raw_triangles = get_raw_triangles(points)
                        voronoi_edges = voronoi_from_delaunay(points, raw_triangles)

    # Отрисовка
    draw_points(points, screen)

    if mode == "Delaunay" and triangles:
        draw_delaunay(triangles, screen)

    if mode == "Voronoi" and voronoi_edges:
        draw_voronoi(voronoi_edges, screen)

    # Кнопки
    btn_clear.draw(screen)
    btn_delaunay.draw(screen, mode == "Delaunay")
    btn_voronoi.draw(screen, mode == "Voronoi")

    # Результат
    if result_text:
        font = pg.font.Font(None, 28)
        txt = font.render(result_text, True, BLACK)
        screen.blit(txt, (280, 15))

    pg.display.flip()
    clock.tick(60)

pg.quit()