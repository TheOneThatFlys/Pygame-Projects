import pygame
from button import Button
from loading import popup_bg, popup_close_button, font, titlefont, descriptionfont
from utils import customFormat
from globals_ import dis

class EarningsPopup(pygame.sprite.Sprite):
    def __init__(self, groups, timeAway: str, income):
        super().__init__(groups["popups"])
        self.dis = dis

        self.image = popup_bg
        self.rect = self.image.get_rect(center = (self.dis.get_width()//2, self.dis.get_height()//2))

        self.closeButton = Button(
            self.rect.centerx,
            self.rect.centery + 50,
            popup_close_button["default"],
            popup_close_button["hover"],
            popup_close_button["pressed"],
            center = True,
            text = ["OK!", descriptionfont, (255, 255, 255)],
            dynamicText = 5
        )

        a = titlefont.render(f"You were away for", True, (255, 255, 255))
        b = titlefont.render(timeAway, True, (255, 255, 255))
        c = titlefont.render(f"and earned", True, (255, 255, 255))
        d = font.render(f"${customFormat(income)}", True, (255, 255, 255))

        self.texts = [
            (a, a.get_rect(center = (self.rect.centerx, self.rect.centery - 70))),
            (b, b.get_rect(center = (self.rect.centerx, self.rect.centery - 50))),
            (c, c.get_rect(center = (self.rect.centerx, self.rect.centery - 30))),
            (d, c.get_rect(center = (self.rect.centerx, self.rect.centery)))
        ]

    def update(self):
        self.dis.blit(self.image, self.rect)
        for surface, rect in self.texts:
            self.dis.blit(surface, rect)
        self.closeButton.update()
        if self.closeButton.isPressed():
            self.kill()