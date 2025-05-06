import pygame
from screens.screen_base import *
from ui import *
import lang_manager



class StartScreen(Screen):
    def __init__(self, font, switch_to_input, switch_to_settings, set_lang):
        super().__init__()
        self.font = font
        self.buttons = [
            Button(lang_manager.translate("start"), 300, 300, 200, 60, switch_to_input, font),
            Button(lang_manager.translate("settings"), 300, 380, 200, 50, switch_to_settings, font),
            Button(lang_manager.translate("langToggle"), 700, 520, 40, 40, set_lang, font, "assets/Picture/langBtn.png"),
        ]
    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)

    def draw(self, screen):
        screen.fill((240, 240, 240))
        title = self.font.render(lang_manager.translate("startTitle"), True, (0, 0, 0))
        screen.blit(title, (self.screeWidth // 2 - title.get_width() // 2, 120))
        for b in self.buttons:
            b.draw(screen)
    def update(self, dt):
        pass
    def enter(self):
        pass
    def exit(self): 
        pass
    