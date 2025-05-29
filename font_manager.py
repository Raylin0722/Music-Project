import pygame, os
from path_manager import path_manager


class FontManager:
    def __init__(self):
        self.fonts = {
            "en": pygame.font.Font(path_manager.get_path("assets", r"fonts\NotoSans-Regular.ttf"), 36),
            "en_italic": pygame.font.Font(path_manager.get_path("assets", r"fonts\NotoSans-Italic.ttf"), 36),
            "zh": pygame.font.Font(path_manager.get_path("assets", r"fonts\NotoSansTC.ttf"), 36)
        }

        print(path_manager.get_path("assets", r"fonts\NotoSans-Regular.ttf"))
        print(path_manager.get_path("assets", r"fonts\NotoSans-Italic.ttf"))
        print(path_manager.get_path("assets", r"fonts\NotoSansTC.ttf"))
        
    def get(self, name):
        return self.fonts.get(name)