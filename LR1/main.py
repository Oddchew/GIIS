import pygame as pg
from button import button
from dda import DDA
from bresenham import bresenham_pixels
from bresenham_circle import bresenham_circle_pixels
SIZE = (1200, 600)
NAME = "Графический редактор"
BLACK = (0,0,0)
WHITE = (255,255,255)
FONT_SIZE = 20
MAX_VALUES_ON_SCREEN = 30
DEBUG_POSITION = (1000, 50)
ByRadius = 1

def draw_line(points, screen):
    for point in points:
        pg.draw.circle(screen, BLACK, point, radius=1)

def draw_debug(points: list, screen: pg.Surface, position: tuple, scroll_offset: int) -> None:
    """
    Отрисовка отладки
    """
    font = pg.font.Font(None, FONT_SIZE)
    field = pg.Rect(position[0], position[1], 150, 500)

    pg.draw.rect(screen, WHITE, field)
    pg.draw.rect(screen, BLACK, field, 3)\

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

button_clear = button((10,50, 180, 50), "Очистить поле")
button_dda = button((10, 110, 180, 50), "ЦДА")
button_bresenhem = button((10, 170, 180, 50), "Брезенхем")
button_By = button((10, 230, 180, 50), "By")
button_debug = button((10, 290, 180,50), "Отладка")

screen = pg.display.set_mode(SIZE)
pg.display.set_caption(NAME)
clock = pg.time.Clock()
field = pg.Rect(200, 50, 700, 500)
lines = []
mode = "DDA"
is_By_pressed = False
is_debug_pressed = False

scroll_offset = 0

start_pos = None
end_pos = None

run = True
while(run):
    screen.fill(color = WHITE)
    pg.draw.rect(screen, WHITE, field)
    pg.draw.rect(screen, BLACK, field, 3) 
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False

        if button_clear.is_press(event=event):
            lines = []
        
        if button_dda.is_press(event=event):
            mode = "DDA"
        
        if button_bresenhem.is_press(event=event):
            mode = "bresengem"
        
        if button_By.is_press(event=event):
            is_By_pressed = not is_By_pressed

        if button_debug.is_press(event=event):
            is_debug_pressed = not is_debug_pressed

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if field.collidepoint(event.pos):
                if start_pos is None:
                    start_pos = event.pos

                elif end_pos is None:
                    end_pos = event.pos

                    if mode == "DDA":
                        points = DDA(start_pos[0], start_pos[1], end_pos[0], end_pos[1])
                        lines.append(points)

                    elif mode == "bresengem":
                        points = bresenham_pixels(start_pos[0], start_pos[1], end_pos[0], end_pos[1])
                        lines.append(points)

                    if is_By_pressed:
                        for point in points:
                            points_circle = bresenham_circle_pixels(point[0], point[1], ByRadius)
                            lines.append(points_circle)
                        
                    #draw_line(points, screen)
                    start_pos = None
                    end_pos = None
                
        if event.type == pg.MOUSEWHEEL:
            if is_debug_pressed:
                scroll_offset -= event.y * 10  
                scroll_offset = max(0, scroll_offset)
                scroll_offset = min(len(lines[-1]) - MAX_VALUES_ON_SCREEN, scroll_offset)
    
    for points in lines:
        draw_line(points, screen)

    button_clear.draw(screen=screen, pressed = False)
    button_dda.draw(screen=screen, pressed = mode == "DDA")
    button_bresenhem.draw(screen=screen, pressed= mode == "bresengem")
    button_By.draw(screen=screen, pressed=is_By_pressed)
    button_debug.draw(screen=screen, pressed= is_debug_pressed)

    if is_debug_pressed and lines:
        points = lines[-1]
        draw_debug(points, screen, position=DEBUG_POSITION, scroll_offset=scroll_offset)

    pg.display.flip()
    clock.tick(60)

pg.quit()
