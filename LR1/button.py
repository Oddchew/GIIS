import pygame as pg
color1 = (100, 200, 100)
color2 = (150, 80, 80)
color3 = (80, 150, 80)
WHITE = (255, 255, 255)
FONT_SIZE = 34

class button:
    """
    Класс реализующий кнопку на pygame
    """
    def __init__(self, rect: pg.Rect, text: str):
        
        self.rect = pg.Rect(rect)
        self.button_font = pg.font.Font(None, FONT_SIZE)
        self.text = self.button_font.render(text, True,WHITE)
    
    def draw(self, screen: pg.Surface, pressed: bool) -> None: 
        """Отрисовка кнопки"""

        if self.rect.collidepoint(pg.mouse.get_pos()):
            color = color1 
        
        elif pressed:
            color = color2

        else: 
            color = color3 

        pg.draw.rect(screen, color, self.rect)
        pg.draw.rect(screen, WHITE, self.rect, 3)

        text_rect = self.text.get_rect(center=self.rect.center)
        screen.blit(self.text, text_rect)

    def is_press(self, event) -> bool:
        """Проверка нажатия кнопки"""

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
            else:
                return False
        else:
            return False