# screens/input_screen.py
import pygame
from screens.screen_base import Screen
from ui import Button
import lang_manager

class InputScreen(Screen):
    def __init__(self, font, switch_to_midi, switch_to_piano, switch_to_mood, switch_to_composer, switch_to_start):
        super().__init__()
        self.font = font
        self.buttons = [
            Button(lang_manager.translate("MIDI_player"), 200, 120, 400, 50, switch_to_midi, font),
            Button(lang_manager.translate("piano_simulator"), 200, 190, 400, 50, switch_to_piano, font),
            Button(lang_manager.translate("random_generator"), 200, 260, 400, 50, switch_to_mood, font),
            Button(lang_manager.translate("composition_feature"), 200, 330, 400, 50, switch_to_composer, font),
            Button(lang_manager.translate("back"), 300, 420, 200, 50, switch_to_start, font)
        ]

    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((230, 230, 230))
        title = self.font.render(lang_manager.translate("select_function"), True, (0, 0, 0))
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 40))
        for b in self.buttons:
            b.draw(screen)
