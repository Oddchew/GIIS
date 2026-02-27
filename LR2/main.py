import pygame as pg
from button import button
from second_order_curves import SecondOrderCurves

SIZE = (1200, 600)
NAME = "Графический редактор"
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
FONT_SIZE = 20
MAX_VALUES_ON_SCREEN = 30
DEBUG_POSITION = (1000, 50)
FIELD_RECT = (200, 50, 700, 500)
SCALE = 10

def position_translator(pos):
    x = int((pos[0] - FIELD_RECT[0]) / SCALE)
    y = int((pos[1] - FIELD_RECT[1]) / SCALE)
    return (x, y)

def draw_grid(screen):
    for x in range(FIELD_RECT[0], FIELD_RECT[0] + FIELD_RECT[2], SCALE):
        pg.draw.line(screen, (200, 200, 200), (x, FIELD_RECT[1]), (x, FIELD_RECT[1] + FIELD_RECT[3]))
    for y in range(FIELD_RECT[1], FIELD_RECT[1] + FIELD_RECT[3], SCALE):
        pg.draw.line(screen, (200, 200, 200), (FIELD_RECT[0], y), (FIELD_RECT[0] + FIELD_RECT[2], y))

def draw_points(points, screen):
    for point in points:
        rect = pg.Rect((FIELD_RECT[0] + SCALE * point[0], FIELD_RECT[1] + SCALE * point[1], SCALE, SCALE))
        if field.collidepoint(rect.center):
            pg.draw.rect(screen, BLACK, rect)

def draw_debug(points: list, screen: pg.Surface, position: tuple, scroll_offset: int) -> None:
    font = pg.font.Font(None, FONT_SIZE)
    field = pg.Rect(position[0], position[1], 150, 500)

    pg.draw.rect(screen, WHITE, field)
    pg.draw.rect(screen, BLACK, field, 3)

    x = font.render("x", True, BLACK)
    y = font.render("y", True, BLACK)

    x_rect = (position[0]+5, position[1]+5, 50, 5)
    y_rect = (position[0]+60, position[1]+5, 50, 5)

    screen.blit(x, x_rect)
    screen.blit(y, y_rect)

    for i in range(scroll_offset, min(scroll_offset + MAX_VALUES_ON_SCREEN, len(points))):
        x_value, y_value = points[i][0], points[i][1]

        x = font.render(str(x_value), True, BLACK)
        y = font.render(str(y_value), True, BLACK)

        x_rect = (position[0]+5, position[1]+20 + 15*(i - scroll_offset), 50, 5)
        y_rect = (position[0]+60, position[1]+20 + 15*(i - scroll_offset), 50, 5)

        screen.blit(x, x_rect)
        screen.blit(y, y_rect)

pg.init()

button_clear = button((10, 50, 180, 50), "Очистить поле")
button_circle = button((10, 110, 180, 50), "Окружность")
button_ellipse = button((10, 170, 180, 50), "Эллипс")
button_hyperbola = button((10, 230, 180, 50), "Гипербола")
button_parabola = button((10, 290, 180, 50), "Парабола")
button_debug = button((10, 350, 180, 50), "Отладка")

screen = pg.display.set_mode(SIZE)
pg.display.set_caption(NAME)
clock = pg.time.Clock()
field = pg.Rect(FIELD_RECT)

curves = SecondOrderCurves()

lines = []
mode = None
is_debug_pressed = False
scroll_offset = 0

center = None
radius = 0
a = 0
b = 0
p = 0

run = True
while run:
    screen.fill(WHITE)
    pg.draw.rect(screen, WHITE, field)
    pg.draw.rect(screen, BLACK, field, 3)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False

        if button_clear.is_press(event=event):
            lines = []
            center = None
            radius = 0
            a = 0
            b = 0
            p = 0

        if button_debug.is_press(event=event):
            is_debug_pressed = not is_debug_pressed

        if button_circle.is_press(event=event):
            mode = "circle"

        if button_ellipse.is_press(event=event):
            mode = "ellipse"

        if button_hyperbola.is_press(event=event):
            mode = "hyperbola"

        if button_parabola.is_press(event=event):
            mode = "parabola"

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if field.collidepoint(event.pos):
                if mode == "circle":
                    if center is None:
                        center = position_translator(event.pos)
                    else:
                        radius_point = position_translator(event.pos)
                        radius = int(((radius_point[0] - center[0]) ** 2 + (radius_point[1] - center[1]) ** 2) ** 0.5)
                        points = curves.bresenham_circle(radius)
                        translated_points = [(point[0] + center[0], point[1] + center[1]) for point in points]
                        lines.append(translated_points)
                        center = None
                        radius = 0

                elif mode == "ellipse":
                    if center is None:
                        center = position_translator(event.pos)
                    else:
                        a = abs(position_translator(event.pos)[0] - center[0])
                        b = abs(position_translator(event.pos)[1] - center[1])
                        points = curves.bresenham_ellipse(a, b)
                        translated_points = [(point[0] + center[0], point[1] + center[1]) for point in points]
                        lines.append(translated_points)
                        center = None
                        a = 0
                        b = 0

                elif mode == "hyperbola":
                    if center is None:
                        center = position_translator(event.pos)
                    else:
                        a = abs(position_translator(event.pos)[0] - center[0]) // 2
                        b = abs(position_translator(event.pos)[1] - center[1]) // 2
                        points = curves.hyperbola(center[0], center[1], a, b)
                        lines.append(points)
                        center = None
                        a = 0
                        b = 0


                elif mode == "parabola":
                    if center is None:
                        center = position_translator(event.pos)
                    else:
                        p = position_translator(event.pos)[0] - center[0]
                        p = abs(p)  # чтобы точно было > 0
                        points = curves.parabola(center[0], center[1], p)
                        lines.append(points)
                        center = None
                        p = 0


                scroll_offset = 0

        if event.type == pg.MOUSEWHEEL:
            if is_debug_pressed and lines:
                scroll_offset -= event.y * 10
                scroll_offset = min(len(lines[-1]) - MAX_VALUES_ON_SCREEN, scroll_offset)
                scroll_offset = max(0, scroll_offset)

    for points in lines:
        draw_points(points, screen)

    button_clear.draw(screen=screen, pressed=False)
    button_circle.draw(screen=screen, pressed=mode == "circle")
    button_ellipse.draw(screen=screen, pressed=mode == "ellipse")
    button_hyperbola.draw(screen=screen, pressed=mode == "hyperbola")
    button_parabola.draw(screen=screen, pressed=mode == "parabola")
    button_debug.draw(screen=screen, pressed=is_debug_pressed)

    if is_debug_pressed:
        draw_grid(screen)
        if lines:
            points = lines[-1]
            draw_debug(points, screen, position=DEBUG_POSITION, scroll_offset=scroll_offset)

    pg.display.flip()
    clock.tick(60)

pg.quit()
