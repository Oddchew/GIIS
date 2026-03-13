import pygame as pg
from button import button
from algoritms import InterpolationCurves


SIZE = (1200, 600)
NAME = "Графический редактор"
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
FONT_SIZE = 20
MAX_VALUES_ON_SCREEN = 30
DEBUG_POSITION = (1000, 50)
FIELD_RECT = (200, 50, 700, 500)
SCALE = 2
SNAP_THRESHOLD = 30  # pixels, increased for easier capture


def position_translator(pos):
    x = int((pos[0] - FIELD_RECT[0]) / SCALE)
    y = int((pos[1] - FIELD_RECT[1]) / SCALE)
    return (x, y)


def pixel_position(point):
    return (
        FIELD_RECT[0] + SCALE * point[0] + SCALE // 2,
        FIELD_RECT[1] + SCALE * point[1] + SCALE // 2,
    )


def dist(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


def draw_grid(screen):
    for x in range(FIELD_RECT[0], FIELD_RECT[0] + FIELD_RECT[2], SCALE):
        pg.draw.line(
            screen,
            (200, 200, 200),
            (x, FIELD_RECT[1]),
            (x, FIELD_RECT[1] + FIELD_RECT[3]),
        )
    for y in range(FIELD_RECT[1], FIELD_RECT[1] + FIELD_RECT[3], SCALE):
        pg.draw.line(
            screen,
            (200, 200, 200),
            (FIELD_RECT[0], y),
            (FIELD_RECT[0] + FIELD_RECT[2], y),
        )


def draw_points(points, screen, color=BLACK, is_controls=False):
    for point in points:
        center = pixel_position(point)
        if field.collidepoint(center):
            if is_controls:
                pg.draw.circle(screen, color, center, 8)
            else:
                rect = pg.Rect(
                    (
                        FIELD_RECT[0] + SCALE * point[0],
                        FIELD_RECT[1] + SCALE * point[1],
                        SCALE,
                        SCALE,
                    )
                )
                pg.draw.rect(screen, color, rect)


def draw_debug(points: list, screen: pg.Surface, position: tuple, scroll_offset: int) -> None:
    font = pg.font.Font(None, FONT_SIZE)
    field_debug = pg.Rect(position[0], position[1], 150, 500)

    pg.draw.rect(screen, WHITE, field_debug)
    pg.draw.rect(screen, BLACK, field_debug, 3)

    x_txt = font.render("x", True, BLACK)
    y_txt = font.render("y", True, BLACK)

    x_rect = (position[0] + 5, position[1] + 5, 50, 5)
    y_rect = (position[0] + 60, position[1] + 5, 50, 5)

    screen.blit(x_txt, x_rect)
    screen.blit(y_txt, y_rect)

    for i in range(scroll_offset, min(scroll_offset + MAX_VALUES_ON_SCREEN, len(points))):
        x_value, y_value = points[i][0], points[i][1]

        x_txt = font.render(str(x_value), True, BLACK)
        y_txt = font.render(str(y_value), True, BLACK)

        x_rect = (position[0] + 5, position[1] + 20 + 15 * (i - scroll_offset), 50, 5)
        y_rect = (position[0] + 60, position[1] + 20 + 15 * (i - scroll_offset), 50, 5)

        screen.blit(x_txt, x_rect)
        screen.blit(y_txt, y_rect)


pg.init()

button_clear = button((10, 50, 180, 50), "Очистить поле")
button_debug = button((10, 110, 180, 50), "Отладка")
button_hermite = button((10, 170, 180, 50), "Эрмит")
button_bezier = button((10, 230, 180, 50), "Безье")
button_bspline = button((10, 290, 180, 50), "B-сплайн")
button_finish = button((10, 350, 180, 50), "Завершить")
button_edit = button((10, 410, 180, 50), "Редактировать")

screen = pg.display.set_mode(SIZE)
pg.display.set_caption(NAME)
clock = pg.time.Clock()
field = pg.Rect(FIELD_RECT)

interp_curves = InterpolationCurves()

curves = []  # list of dict {'type': str, 'controls': list, 'points': list}
mode = None
is_debug_pressed = False
is_edit_pressed = False
scroll_offset = 0
current_controls = []
selected = None  # (curve_idx, control_idx)

# новое: флаги драга
dragging = False
drag_offset = (0, 0)

run = True
while run:
    screen.fill(WHITE)
    pg.draw.rect(screen, WHITE, field)
    pg.draw.rect(screen, BLACK, field, 3)

    mouse_pos = pg.mouse.get_pos()
    mouse_pressed = pg.mouse.get_pressed()[0]

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False

        if button_clear.is_press(event=event):
            curves = []
            current_controls = []

        if button_debug.is_press(event=event):
            is_debug_pressed = not is_debug_pressed

        if button_edit.is_press(event=event):
            is_edit_pressed = not is_edit_pressed
            selected = None
            dragging = False

        if button_hermite.is_press(event=event):
            mode = "hermite"
            current_controls = []

        if button_bezier.is_press(event=event):
            mode = "bezier"
            current_controls = []

        if button_bspline.is_press(event=event):
            mode = "bspline"
            current_controls = []

        # Режим ввода новых точек (когда не редактируем)
        if not is_edit_pressed:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if field.collidepoint(event.pos):
                    pos = position_translator(event.pos)
                    if mode in ["hermite", "bezier", "bspline"]:
                        current_controls.append(pos)

        # Завершение кривой и генерация точек
        if button_finish.is_press(event=event):
            if mode == "hermite":
                if len(current_controls) >= 4:
                    P1 = current_controls[0]
                    R1_p = current_controls[1]
                    P4 = current_controls[2]
                    R4_p = current_controls[3]
                    R1 = (R1_p[0] - P1[0], R1_p[1] - P1[1])
                    R4 = (R4_p[0] - P4[0], R4_p[1] - P4[1])
                    points = interp_curves.hermite(P1, R1, P4, R4)
                    curves.append(
                        {
                            "type": "hermite",
                            "controls": current_controls[:],
                            "points": points,
                        }
                    )
                    current_controls = []
                    scroll_offset = 0
            elif mode == "bezier":
                if len(current_controls) >= 4:
                    points = interp_curves.bezier(*current_controls[:4])
                    curves.append(
                        {
                            "type": "bezier",
                            "controls": current_controls[:4],
                            "points": points,
                        }
                    )
                    current_controls = []
                    scroll_offset = 0
            elif mode == "bspline":
                if len(current_controls) >= 4:
                    points = interp_curves.b_spline(current_controls)
                    curves.append(
                        {
                            "type": "bspline",
                            "controls": current_controls[:],
                            "points": points,
                        }
                    )
                    current_controls = []
                    scroll_offset = 0

        # Скролл отладочной панели
        if event.type == pg.MOUSEWHEEL:
            if is_debug_pressed and curves:
                scroll_offset -= event.y * 10
                scroll_offset = min(
                    len(curves[-1]["points"]) - MAX_VALUES_ON_SCREEN, scroll_offset
                )
                scroll_offset = max(0, scroll_offset)

        # --- РЕЖИМ РЕДАКТИРОВАНИЯ: выбор точки для драга ---
        if is_edit_pressed and event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if field.collidepoint(event.pos):
                click_pos = event.pos
                min_dist = float("inf")
                selected = None
                for c_idx, curve in enumerate(curves):
                    if curve["type"] in ["hermite", "bezier", "bspline"]:
                        for p_idx, point in enumerate(curve["controls"]):
                            point_pixel = pixel_position(point)
                            d = dist(click_pos, point_pixel)
                            if d < min_dist:
                                min_dist = d
                                selected = (c_idx, p_idx)
                if min_dist <= SNAP_THRESHOLD:
                    dragging = True
                    curve = curves[selected[0]]
                    pt = curve["controls"][selected[1]]
                    pt_pix = pixel_position(pt)
                    drag_offset = (pt_pix[0] - click_pos[0], pt_pix[1] - click_pos[1])
                else:
                    selected = None
                    dragging = False

        # --- РЕЖИМ РЕДАКТИРОВАНИЯ: перетаскивание точки ---
        if is_edit_pressed and event.type == pg.MOUSEMOTION and dragging and selected is not None:
            pos = (event.pos[0] + drag_offset[0], event.pos[1] + drag_offset[1])

            # координата в системе поля
            snap_coord = position_translator(pos)
            min_snap_dist = float("inf")

            # привязка к точкам других кривых (controls и points)
            for c_idx, curve in enumerate(curves):
                if c_idx != selected[0]:
                    for point in curve["controls"]:
                        point_pixel = pixel_position(point)
                        d = dist(pos, point_pixel)
                        if d < min_snap_dist and d < SNAP_THRESHOLD:
                            min_snap_dist = d
                            snap_coord = point
                    for point in curve["points"]:
                        point_pixel = pixel_position(point)
                        d = dist(pos, point_pixel)
                        if d < min_snap_dist and d < SNAP_THRESHOLD:
                            min_snap_dist = d
                            snap_coord = point

            # обновляем контрольную точку
            curves[selected[0]]["controls"][selected[1]] = snap_coord

            # пересчёт кривой
            curve = curves[selected[0]]
            typ = curve["type"]
            controls = curve["controls"]
            if typ == "hermite":
                P1 = controls[0]
                R1_p = controls[1]
                P4 = controls[2]
                R4_p = controls[3]
                R1 = (R1_p[0] - P1[0], R1_p[1] - P1[1])
                R4 = (R4_p[0] - P4[0], R4_p[1] - P4[1])
                curve["points"] = interp_curves.hermite(P1, R1, P4, R4)
            elif typ == "bezier":
                curve["points"] = interp_curves.bezier(*controls)
            elif typ == "bspline":
                curve["points"] = interp_curves.b_spline(controls)

        # --- РЕЖИМ РЕДАКТИРОВАНИЯ: отпускание точки ---
        if is_edit_pressed and event.type == pg.MOUSEBUTTONUP and event.button == 1:
            dragging = False
            selected = None

    # Отрисовка кривых
    for curve in curves:
        draw_points(curve["points"], screen)

    # Отрисовка опорных точек
    if not is_edit_pressed:
        draw_points(current_controls, screen, color=RED, is_controls=True)
    else:
        for curve in curves:
            draw_points(curve["controls"], screen, color=RED, is_controls=True)

    # Кнопки
    button_clear.draw(screen=screen, pressed=False)
    button_debug.draw(screen=screen, pressed=is_debug_pressed)
    button_hermite.draw(screen=screen, pressed=mode == "hermite")
    button_bezier.draw(screen=screen, pressed=mode == "bezier")
    button_bspline.draw(screen=screen, pressed=mode == "bspline")
    button_finish.draw(screen=screen, pressed=False)
    button_edit.draw(screen=screen, pressed=is_edit_pressed)

    # Отладка
    if is_debug_pressed:
        draw_grid(screen)
        if curves:
            points = curves[-1]["points"]
            draw_debug(
                points,
                screen,
                position=DEBUG_POSITION,
                scroll_offset=scroll_offset,
            )

    pg.display.flip()
    clock.tick(60)

pg.quit()
