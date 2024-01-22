import pygame
from button import Button
from loading import menu_bg, play_button, exit_button
from globals_ import dis, currentScreen

class Menu():
    def __init__(self):
        self.dis = dis

        self.playButton = Button(350, 300, play_button["default"], play_button["hover"], play_button["pressed"], center=True)
        self.exitButton = Button(10, 400, exit_button["default"], exit_button["hover"], exit_button["pressed"])

    def run(self):
        self.dis.blit(menu_bg, (0, 0))
        self.playButton.update()
        self.exitButton.update()

        if self.playButton.isPressed():
            currentScreen.value = "level"
        if self.exitButton.isPressed():
            currentScreen.value = "exit"