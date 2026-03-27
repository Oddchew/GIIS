import pygame as pg
from button import button
from algorithms import point_in_polygon
from fill_algorithms import (
    scanline_edge_table,
    scanline_active_edge,
    flood_fill_simple,
    flood_fill_scanline
)
from drawer import (
    draw_polygons,
    draw_current_polygon,
    draw_filled_pixels,
    draw_debug_fill,
    draw_grid
)
from consts import (
    SIZE, NAME, BLACK, WHITE, SCALE, FIELD_RECT,
    FONT_SIZE, DEBUG_POSITION
)

def position_translator(pos):
    x = int((pos[0] - FIELD_RECT[0]) / SCALE)
    y = int((pos[1] - FIELD_RECT[1]) / SCALE)
    return (x, y)

def draw_debug(points: list, screen: pg.Surface, position: tuple, scroll_offset: int) -> None:
    font = pg.font.Font(None, FONT_SIZE)
    field = pg.Rect(position[0], position[1], 150, 500)
    pg.draw.rect(screen, WHITE, field)
    pg.draw.rect(screen, BLACK, field, 3)
    x = font.render("x", True, BLACK)
    y = font.render("y", True, BLACK)
    screen.blit(x, (position[0] + 5, position[1] + 5))
    screen.blit(y, (position[0] + 60, position[1] + 5))
    for i in range(scroll_offset, min(scroll_offset + 25, len(points))):
        xv, yv = points[i]
        screen.blit(font.render(str(xv), True, BLACK), (position[0] + 5, position[1] + 20 + 18 * (i - scroll_offset)))
        screen.blit(font.render(str(yv), True, BLACK), (position[0] + 60, position[1] + 20 + 18 * (i - scroll_offset)))

pg.init()

button_clear = button((10, 50, 180, 50), "Очистить поле")
button_debug = button((10, 110, 180, 50), "Отладка")

button_polygon = button((10, 180, 180, 50), "Полигон")
button_close_poly = button((10, 240, 180, 50), "Замкнуть полигон")

button_scan_et = button((10, 320, 180, 50), "Scan ET")
button_scan_aet = button((10, 380, 180, 50), "Scan AET")
button_flood_simple = button((10, 440, 180, 50), "Затравка простая")
button_flood_scan = button((10, 500, 180, 50), "Затравка построчная")

screen = pg.display.set_mode(SIZE)
pg.display.set_caption(NAME)
clock = pg.time.Clock()

field = pg.Rect(FIELD_RECT)

polygons = []                    # все замкнутые полигоны
current_polygon = []
filled_history = []              # список заполнений: [(pixels, color), ...]
debug_info = None

mode = "polygon"
fill_mode = None
is_debug_pressed = False
scroll_offset = 0
result_text = ""

run = True
while run:
    screen.fill(WHITE)
    pg.draw.rect(screen, WHITE, field)
    pg.draw.rect(screen, BLACK, field, 3)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False

        if button_clear.is_press(event):
            polygons.clear()
            current_polygon.clear()
            filled_history.clear()
            debug_info = None
            result_text = ""

        if button_debug.is_press(event):
            is_debug_pressed = not is_debug_pressed

        if button_polygon.is_press(event):
            mode = "polygon"
            fill_mode = None
            current_polygon.clear()
            result_text = "Режим: построение полигона"

        if button_close_poly.is_press(event):
            if len(current_polygon) >= 3:
                polygons.append(current_polygon[:])
                current_polygon.clear()
                result_text = "Полигон замкнут"

        # Выбор алгоритма
        if button_scan_et.is_press(event):
            fill_mode = "scan_et"
            mode = "fill"
            result_text = "Выбран: Scan ET"
        if button_scan_aet.is_press(event):
            fill_mode = "scan_aet"
            mode = "fill"
            result_text = "Выбран: Scan AET"
        if button_flood_simple.is_press(event):
            fill_mode = "flood_simple"
            mode = "fill"
            result_text = "Выбран: простая затравка"
        if button_flood_scan.is_press(event):
            fill_mode = "flood_scan"
            mode = "fill"
            result_text = "Выбран: построчная затравка"

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if field.collidepoint(event.pos):
                pos = position_translator(event.pos)

                if mode == "polygon":
                    current_polygon.append(pos)

                # Заполнение полигона
                elif mode == "fill" and polygons:
                    poly = polygons[-1]
                    debug_info = None
                    new_filled = []

                    if fill_mode == "scan_et":
                        new_filled, debug_info = scanline_edge_table(poly, debug=is_debug_pressed)
                    elif fill_mode == "scan_aet":
                        new_filled, debug_info = scanline_active_edge(poly, debug=is_debug_pressed)
                    elif fill_mode == "flood_simple":
                        if point_in_polygon(pos, poly):
                            new_filled, debug_info = flood_fill_simple(poly, pos, debug=is_debug_pressed)
                        else:
                            result_text = "Точка вне полигона"
                            continue
                    elif fill_mode == "flood_scan":
                        if point_in_polygon(pos, poly):
                            new_filled, debug_info = flood_fill_scanline(poly, pos, debug=is_debug_pressed)
                        else:
                            result_text = "Точка вне полигона"
                            continue

                    # Добавляем старое заполнение как "чёрное"
                    if filled_history:
                        old_pixels, _ = filled_history[-1]
                        filled_history[-1] = (old_pixels, (50, 50, 50))  # тёмно-серый / чёрный

                    # Добавляем новое заполнение цветным
                    filled_history.append((new_filled, (220, 80, 80)))   # красноватый
                    result_text = f"{fill_mode}: {len(new_filled)} пикселей"

        if event.type == pg.MOUSEWHEEL and is_debug_pressed and polygons:
            scroll_offset -= event.y * 10
            scroll_offset = max(0, scroll_offset)
            scroll_offset = min(len(polygons[-1]) - 25, scroll_offset)

    # ==================== ОТРИСОВКА ====================
    draw_polygons(polygons, screen)
    draw_current_polygon(current_polygon, screen)

    # Отрисовка всех заполнений с их цветами
    for pixels, color in filled_history:
        draw_filled_pixels(pixels, screen, color=color)

    # Кнопки
    button_clear.draw(screen, False)
    button_debug.draw(screen, is_debug_pressed)
    button_polygon.draw(screen, mode == "polygon")
    button_close_poly.draw(screen, False)

    button_scan_et.draw(screen, fill_mode == "scan_et")
    button_scan_aet.draw(screen, fill_mode == "scan_aet")
    button_flood_simple.draw(screen, fill_mode == "flood_simple")
    button_flood_scan.draw(screen, fill_mode == "flood_scan")

    if result_text:
        font = pg.font.Font(None, 26)
        txt = font.render(result_text, True, BLACK)
        screen.blit(txt, (220, 10))

    if is_debug_pressed:
        draw_grid(screen)
        if polygons:
            draw_debug(polygons[-1], screen, DEBUG_POSITION, scroll_offset)
        if debug_info:
            draw_debug_fill(debug_info, screen)

    pg.display.flip()
    clock.tick(60)

pg.quit()