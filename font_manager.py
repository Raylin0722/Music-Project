import pygame


class FontManager:
    def __init__(self):
        self.fonts = {
            "en": pygame.font.Font("assets/fonts/NotoSans-Regular.ttf", 36),
            "en_italic": pygame.font.Font("assets/fonts/NotoSans-Italic.ttf", 36),
            "zh": pygame.font.Font("assets/fonts/NotoSansTC.ttf", 36)
        }

    def get(self, name):
        return self.fonts.get(name)