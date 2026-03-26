import pygame as pg
from drawer import draw_intersections, draw_normals, draw_point_check, draw_polygons, draw_pts, draw_current_polygon
from button import button
from dda import DDA
from bresenham import bresenham_pixels
from bresenham_circle import draw_by_line
from algorithms import (
    is_convex, get_internal_normals, graham_scan, jarvis_march,
    point_in_polygon, segment_polygon_intersections
)
from consts import FIELD_RECT, SCALE, BLACK, WHITE, GREEN, RED, FONT_SIZE, MAX_VALUES_ON_SCREEN, SIZE, NAME, DEBUG_POSITION

def position_translator(pos):
    x = int((pos[0] - FIELD_RECT[0]) / SCALE)
    y = int((pos[1] - FIELD_RECT[1]) / SCALE)
    return (x, y)

def draw_grid(screen):
    for x in range(FIELD_RECT[0], FIELD_RECT[0] + FIELD_RECT[2], SCALE):
        pg.draw.line(screen, (200, 200, 200), (x, FIELD_RECT[1]), (x, FIELD_RECT[1] + FIELD_RECT[3]))
    for y in range(FIELD_RECT[1], FIELD_RECT[1] + FIELD_RECT[3], SCALE):
        pg.draw.line(screen, (200, 200, 200), (FIELD_RECT[0], y), (FIELD_RECT[0] + FIELD_RECT[2], y))

def draw_debug(points: list, screen: pg.Surface, position: tuple, scroll_offset: int) -> None:
    font = pg.font.Font(None, FONT_SIZE)
    field = pg.Rect(position[0], position[1], 150, 500)
    pg.draw.rect(screen, WHITE, field)
    pg.draw.rect(screen, BLACK, field, 3)
    x = font.render("x", True, BLACK)
    y = font.render("y", True, BLACK)
    screen.blit(x, (position[0] + 5, position[1] + 5))
    screen.blit(y, (position[0] + 60, position[1] + 5))
    for i in range(scroll_offset, min(scroll_offset + MAX_VALUES_ON_SCREEN, len(points))):
        x_value, y_value = points[i][0], points[i][1]
        x_txt = font.render(str(x_value), True, BLACK)
        y_txt = font.render(str(y_value), True, BLACK)
        screen.blit(x_txt, (position[0] + 5, position[1] + 20 + 15 * (i - scroll_offset)))
        screen.blit(y_txt, (position[0] + 60, position[1] + 20 + 15 * (i - scroll_offset)))

pg.init()

button_clear = button((10, 50, 250, 50), "Очистить поле")
button_dda = button((10, 110, 250, 50), "ЦДА")
button_bresenhem = button((10, 170, 250, 50), "Брезенхем")
button_By = button((10, 230, 250, 50), "By")
button_debug = button((10, 290, 250, 50), "Отладка")

button_polygon = button((10, 350, 250, 50), "Полигон")
button_close_poly = button((10, 410, 250, 50), "Замкнуть полигон")
button_convex = button((10, 470, 250, 50), "Выпуклость")
button_normals = button((10, 530, 250, 50), "Нормали")
button_graham = button((10, 590, 250, 50), "Грэхем")
button_jarvis = button((10, 650, 250, 50), "Джарвис")
button_point_in = button((10, 710, 250, 50), "Точка в полигоне")

screen = pg.display.set_mode(SIZE)
pg.display.set_caption(NAME)
clock = pg.time.Clock()

field = pg.Rect(FIELD_RECT)
lines: list[list[tuple[int, int]]] = []          
polygons: list[list[tuple[int, int]]] = []      
current_polygon: list[tuple[int, int]] = []     

mode = "DDA"
is_debug_pressed = False
is_normals = False
scroll_offset = 0
result_text = ""

start_pos = None
end_pos = None
intersections = []
last_point_check = None
point_check_inside = False

run = True
while run:
    screen.fill(WHITE)
    pg.draw.rect(screen, WHITE, field)
    pg.draw.rect(screen, BLACK, field, 3)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False

        if button_clear.is_press(event):
            lines.clear()
            polygons.clear()
            current_polygon.clear()
            intersections.clear()
            result_text = ""

        if button_dda.is_press(event): mode = "DDA"
        if button_bresenhem.is_press(event): mode = "bresenhem"
        if button_By.is_press(event): mode = "By"
        if button_debug.is_press(event):
            is_debug_pressed = not is_debug_pressed

        if button_polygon.is_press(event):
            mode = "polygon"
            current_polygon.clear()

        if button_close_poly.is_press(event):
            if len(current_polygon) >= 3:
                polygons.append(current_polygon[:])
                current_polygon.clear()

        if button_convex.is_press(event) and polygons:
            convex = is_convex(polygons[-1])
            result_text = f"Выпуклый: {'Да' if convex else 'Нет'}"

        if button_normals.is_press(event):
            is_normals = not is_normals

        if button_graham.is_press(event) and polygons:
            hull = graham_scan(polygons[-1][:])
            if len(hull) >= 3:
                polygons.append(hull)
                result_text = "Оболочка Грэхема построена"

        if button_jarvis.is_press(event) and polygons:
            hull = jarvis_march(polygons[-1][:])
            if len(hull) >= 3:
                polygons.append(hull)
                result_text = "Оболочка Джарвиса построена"

        if button_point_in.is_press(event):
            mode = "point_in"
            result_text = "Кликните точку"

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if field.collidepoint(event.pos):
                pos = position_translator(event.pos)

                if mode == "polygon":
                    current_polygon.append(pos)

                elif mode == "point_in" and polygons:
                    last_point_check = pos
                    point_check_inside = point_in_polygon(pos, polygons[-1])
                    result_text = f"Точка {'внутри' if point_check_inside else 'снаружи'}"

                elif mode in ("DDA", "bresenhem", "By"):
                    if start_pos is None:
                        start_pos = pos
                    elif end_pos is None:
                        end_pos = pos
                        if mode == "DDA":
                            pts = DDA(start_pos[0], start_pos[1], end_pos[0], end_pos[1])
                        elif mode == "bresenhem":
                            pts = bresenham_pixels(start_pos[0], start_pos[1], end_pos[0], end_pos[1])
                        else:
                            pts = draw_by_line(start_pos[0], start_pos[1], end_pos[0], end_pos[1])
                        lines.append(pts)

                        if polygons:
                            intersections = segment_polygon_intersections(start_pos, end_pos, polygons[-1])

                        start_pos = None
                        end_pos = None

        if event.type == pg.MOUSEWHEEL and is_debug_pressed and polygons:
            scroll_offset -= event.y * 10
            scroll_offset = max(0, scroll_offset)
            scroll_offset = min(len(polygons[-1]) - MAX_VALUES_ON_SCREEN, scroll_offset)


    draw_pts(lines, screen)

    draw_polygons(polygons, screen)

    draw_current_polygon(current_polygon, screen)

    if is_normals and polygons:
        normals = get_internal_normals(polygons[-1])
        draw_normals(normals, screen)

    draw_intersections(intersections, screen)

    draw_point_check(last_point_check, point_check_inside, screen)

    button_clear.draw(screen, False)
    button_dda.draw(screen, mode == "DDA")
    button_bresenhem.draw(screen, mode == "bresenhem")
    button_By.draw(screen, mode == "By")
    button_debug.draw(screen, is_debug_pressed)
    button_polygon.draw(screen, mode == "polygon")
    button_close_poly.draw(screen, False)
    button_convex.draw(screen, False)
    button_normals.draw(screen, is_normals)
    button_graham.draw(screen, False)
    button_jarvis.draw(screen, False)
    button_point_in.draw(screen, mode == "point_in")

    if is_debug_pressed and polygons:
        draw_grid(screen)
        draw_debug(polygons[-1], screen, DEBUG_POSITION, scroll_offset)

    if result_text:
        font = pg.font.Font(None, 28)
        txt = font.render(result_text, True, BLACK)
        screen.blit(txt, (220, 10))

    pg.display.flip()
    clock.tick(60)

pg.quit()