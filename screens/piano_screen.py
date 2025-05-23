import pygame
import fluidsynth
import time
import lang_manager, config_manager

from screens.screen_base import Screen

WHITE_KEYS = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k']
BLACK_KEYS = ['w', 'e', 'r', 't', 'y']
WHITE_OFFSETS = [0, 2, 4, 5, 7, 9, 11, 12]
BLACK_OFFSETS = [1, 3, 6, 8, 10]
KEY_TO_LABEL = {
    'a': 'C', 'w': 'C#',
    's': 'D', 'e': 'D#',
    'd': 'E',
    'f': 'F', 'r': 'F#',
    'g': 'G', 't': 'G#',
    'h': 'A', 'y': 'A#',
    'j': 'B',
    'k': 'C'
}

MIN_MIDI = 21
MAX_MIDI = 108

class PianoScreen(Screen):
    def __init__(self, font, on_back, on_settings):
        super().__init__()
        self.font = font
        self.on_back = on_back
        self.on_settings = on_settings

        self.fs = fluidsynth.Synth()
        self.fs.start()
        self.sfid = self.fs.sfload("assets/sounds/Antares_SoundFont.sf2")
        self.fs.program_select(0, self.sfid, 0, 0)

        self.base_note = 60  # C4
        self.active_notes = {}
        self.recording = False
        self.record_start_time = None
        self.recorded_notes = {}
        self.rest_recording_mode = config_manager.get_config("rest_mode")
        self.last_record_time = 0.0

        from ui import Button
        self.buttons = [
            Button(lang_manager.translate("back"), 30, 30, 50, 50, on_back, font, 'assets/picture/back.png'),
            Button(lang_manager.translate("record"), 670, 30, 50, 50, self.toggle_recording, font, 'assets/picture/record.png'),
            Button(lang_manager.translate("settings"), 720, 30, 50, 50, on_settings, font, 'assets/picture/settings.png')
        ]

    def toggle_recording(self):
        self.recording = not self.recording
        if self.recording:
            self.record_start_time = time.time()
            self.recorded_notes.clear()
            self.last_record_time = 0.0
            print("🔴 Recording started")
        else:
            print("⏹ Recording stopped")

    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:
                self.shift_octave(-1)
            elif event.key == pygame.K_x:
                self.shift_octave(1)

    def update(self, dt):
        now = time.time()
        keys = pygame.key.get_pressed()
        new_active_notes = {}
        played_now = []

        for i, k in enumerate(WHITE_KEYS):
            note = self.base_note + WHITE_OFFSETS[i]
            if keys[getattr(pygame, f'K_{k}')]:
                new_active_notes[k] = note
                if k not in self.active_notes:
                    self.fs.noteon(0, note, 100)
                    if self.recording:
                        played_now.append(note)
            elif k in self.active_notes:
                self.fs.noteoff(0, self.active_notes[k][0])

        for i, k in enumerate(BLACK_KEYS):
            note = self.base_note + BLACK_OFFSETS[i]
            if keys[getattr(pygame, f'K_{k}')]:
                new_active_notes[k] = note
                if k not in self.active_notes:
                    self.fs.noteon(0, note, 100)
                    if self.recording:
                        played_now.append(note)
            elif k in self.active_notes:
                self.fs.noteoff(0, self.active_notes[k][0])

        # 自動補休止符
        if self.recording:
            now_offset = now - self.record_start_time
            if hasattr(self, 'last_record_time'):
                gap = now_offset - self.last_record_time
                if gap > 0.2 and len(played_now) > 0 and self.rest_recording_mode:
                    self.recorded_notes.append({"note": "rest", "start": self.last_record_time, "duration": gap})
            if played_now:
                for n in played_now:
                    self.recorded_notes.append({"note": n, "start": now_offset, "duration": 0.5})
                self.last_record_time = now_offset

        self.active_notes = {k: (note, now) for k, note in new_active_notes.items()}
        
    
    def shift_octave(self, direction):
        new_base = self.base_note + direction * 12
        if MIN_MIDI <= new_base <= MAX_MIDI - 12:
            self.base_note = new_base

    def midi_to_name(self, midi_num):
        names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        return f"{names[midi_num % 12]}{(midi_num // 12) - 1}"

    def draw(self, screen):
        screen.fill((255, 255, 255))
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        margin = 30

        total_white_keys = len(WHITE_KEYS)
        key_width = (screen_width - 2 * margin) // total_white_keys
        key_height = 300
        x_offset = margin
        y_offset = screen_height - key_height - margin

        # 畫白鍵
        for i, k in enumerate(WHITE_KEYS):
            x = x_offset + i * key_width
            rect = pygame.Rect(x, y_offset, key_width, key_height)
            pygame.draw.rect(screen, (255, 255, 255), rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 2)

            label = self.font.render(KEY_TO_LABEL[k], True, (0, 0, 0))
            screen.blit(label, (x + key_width // 2 - label.get_width() // 2, y_offset + key_height - 60))

            key_label = self.font.render(k.upper(), True, (100, 100, 100))
            screen.blit(key_label, (x + key_width // 2 - key_label.get_width() // 2, y_offset + key_height - 110))

        # 畫黑鍵
        black_key_width = key_width // 2
        black_key_height = int(key_height * 0.6)
        black_key_positions = [0, 1, 3, 4, 5]

        for i, k in enumerate(BLACK_KEYS):
            white_index = black_key_positions[i]
            x = x_offset + (white_index + 1) * key_width - black_key_width // 2
            rect = pygame.Rect(x, y_offset, black_key_width, black_key_height)
            pygame.draw.rect(screen, (0, 0, 0), rect)

            label = self.font.render(KEY_TO_LABEL[k], True, (255, 255, 255))
            screen.blit(label, (x + (black_key_width - label.get_width()) // 2, y_offset + black_key_height - 50))

            key_label = self.font.render(k.upper(), True, (200, 200, 200))
            screen.blit(key_label, (x + (black_key_width - key_label.get_width()) // 2, y_offset + black_key_height - 90))

        # 畫面標題
        title = self.font.render(lang_manager.translate("piano_simulator_title"), True, (0, 0, 0))
        screen.blit(title, (screen_width // 2 - title.get_width() // 2, 30))

        # 顯示音域
        low_note = self.midi_to_name(self.base_note)
        high_note = self.midi_to_name(self.base_note + 12)
        range_text = self.font.render(f"{lang_manager.translate('current_range')} {low_note} ~ {high_note}", True, (0, 0, 0))
        screen.blit(range_text, (30, 80))

        # 顯示播放中音
        current = [self.midi_to_name(n[0]) for n in self.active_notes.values()]
        now_text = self.font.render(f"{lang_manager.translate('currently_playing')} {', '.join(current)}", True, (50, 50, 200))
        screen.blit(now_text, (30, 130))

        for b in self.buttons:
            b.draw(screen)
