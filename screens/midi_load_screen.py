import pygame
import os
from tkinter import filedialog, Tk
from screens.screen_base import Screen
from ui import Button
import lang_manager

class MidiLoadScreen(Screen):
    def __init__(self, font, on_next, on_back):
        super().__init__()
        self.font = font
        self.on_next = on_next  # 進入編輯畫面 callback（會接收 midi_path）
        self._on_back_raw = on_back
        self.midi_path = None
        self.status_text = lang_manager.translate("no_file_selected")
        self.is_playing = False

        center_x = 800 // 2
        self.select_button = Button(lang_manager.translate("select_midi"), center_x - 200, 100, 400, 50, self.load_file, font)
        self.play_pause_button = Button(lang_manager.translate("play"), center_x - 200, 170, 190, 50, self.toggle_play_pause, font)
        self.stop_button = Button(lang_manager.translate("stop"), center_x + 10, 170, 190, 50, self.stop_midi, font)
        self.next_button = Button(lang_manager.translate("next"), center_x - 200, 250, 400, 50, self.next_step, font)
        self.back_button = Button(lang_manager.translate("back"), center_x - 200, 320, 400, 50, self.back_with_stop, font)

        self.buttons = [
            self.select_button,
            self.play_pause_button,
            self.stop_button,
            self.next_button,
            self.back_button
        ]

    def load_file(self):
        Tk().withdraw()
        path = filedialog.askopenfilename(filetypes=[("MIDI files", "*.mid *.midi")])
        if path:
            self.midi_path = path
            self.status_text = f"{lang_manager.translate('file_loaded')}: {os.path.basename(path)}"

    def toggle_play_pause(self):
        if not self.midi_path:
            return
        if not self.is_playing:
            if pygame.mixer.music.get_pos() > 0:
                pygame.mixer.music.unpause()
            else:
                pygame.mixer.music.load(self.midi_path)
                pygame.mixer.music.play()
            self.status_text = lang_manager.translate("playing")
            self.play_pause_button.text = lang_manager.translate("pause")
            self.is_playing = True
        else:
            pygame.mixer.music.pause()
            self.status_text = lang_manager.translate("paused")
            self.play_pause_button.text = lang_manager.translate("play")
            self.is_playing = False

    def stop_midi(self):
        pygame.mixer.music.stop()
        self.status_text = lang_manager.translate("stopped")
        self.play_pause_button.text = lang_manager.translate("play")
        self.is_playing = False

    def next_step(self):
        print("change to composer")
        if self.midi_path:
            self.stop_midi()
            self.on_next(self.midi_path)

    def back_with_stop(self):
        self.stop_midi()
        self.midi_path = None
        self.status_text = lang_manager.translate("no_file_selected")
        self.play_pause_button.text = lang_manager.translate("play")
        self.is_playing = False
        self._on_back_raw()

    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((230, 230, 230))
        for b in self.buttons:
            b.draw(screen)
        status = self.font.render(self.status_text, True, (0, 0, 0))
        screen.blit(status, (800 // 2 - status.get_width() // 2, 400))
