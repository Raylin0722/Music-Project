import pygame
from music21 import converter, instrument
from screens.screen_base import Screen
from ui import Button
import lang_manager
import os

class MidiComposerScreen(Screen):
    def __init__(self, font, midi_path, on_back):
        super().__init__()
        self.font = font
        self.midi_path = midi_path
        self.on_back = on_back
        self.status_text = f"編輯中：{os.path.basename(midi_path)}"

        # 讀取 MIDI 音軌與樂器資訊
        self.score = converter.parse(midi_path)
        self.part_names = []
        self.instrument_names = []

        # MIDI program fallback map
        self.midi_program_map = {
            0: "Acoustic Grand Piano",
            1: "Bright Acoustic Piano",
            24: "Acoustic Guitar (nylon)",
            25: "Acoustic Guitar (steel)",
            26: "Electric Guitar (jazz)",
            27: "Electric Guitar (clean)",
            28: "Electric Guitar (muted)",
            29: "Overdriven Guitar",
            30: "Distortion Guitar",
            31: "Guitar Harmonics",
            33: "Electric Bass (finger)",
            34: "Electric Bass (pick)",
            35: "Fretless Bass",
            36: "Slap Bass 1",
            37: "Slap Bass 2",
            38: "Synth Bass 1",
            39: "Synth Bass 2"
        }
        
        from mido import MidiFile
        midi = MidiFile(midi_path)
        print("========== MIDO 樂器資訊檢查 ==========")
        for i, track in enumerate(midi.tracks):
            print(f"Track {i}:")
            for msg in track:
                if msg.type == 'program_change':
                    print(f"  Program change → Program {msg.program} on channel {msg.channel}")

        for part in self.score.parts:
            instr = part.getInstrument(returnDefault=True)
            self.part_names.append(part.partName or instr.instrumentName or "Unknown")
            fallback = self.midi_program_map.get(getattr(instr, 'midiProgram', -1), "Unknown")
            self.instrument_names.append(instr.instrumentName or fallback)

        self.selected_index = 0

        center_x = 800 // 2
        self.back_button = Button(lang_manager.translate("back"), center_x - 200, 500, 400, 50, on_back, font)
        self.prev_button = Button("←", center_x - 160, 300, 50, 50, self.prev_part, font)
        self.next_button = Button("→", center_x + 110, 300, 50, 50, self.next_part, font)

        self.buttons = [
            self.back_button,
            self.prev_button,
            self.next_button
        ]

    def prev_part(self):
        if self.selected_index > 0:
            self.selected_index -= 1

    def next_part(self):
        if self.selected_index < len(self.part_names) - 1:
            self.selected_index += 1

    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((255, 255, 255))
        title = self.font.render("MIDI 編輯器", True, (0, 0, 0))
        screen.blit(title, (800 // 2 - title.get_width() // 2, 40))

        status = self.font.render(self.status_text, True, (0, 0, 0))
        screen.blit(status, (800 // 2 - status.get_width() // 2, 90))

        if self.part_names:
            name = self.part_names[self.selected_index]
            instr = self.instrument_names[self.selected_index]
            label = f"音軌 {self.selected_index + 1}：{name}（{instr}）"
        else:
            label = "無音軌"

        label_surface = self.font.render(label, True, (0, 0, 128))
        screen.blit(label_surface, (800 // 2 - label_surface.get_width() // 2, 240))

        for b in self.buttons:
            b.draw(screen)
