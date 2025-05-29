import pygame
import fluidsynth
import time
import lang_manager, config_manager
import mido
import os

from screens.screen_base import Screen
from path_manager import path_manager  # 這樣導入的是模組中的實例

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
        sf2_path = path_manager.get_asset("sounds/Antares_SoundFont.sf2")
        self.sfid = self.fs.sfload(sf2_path)
        self.fs.program_select(0, self.sfid, 0, 0)

        self.base_note = 60  # C4
        self.active_notes = {}
        self.recording = False
        self.record_start_time = None
        self.recorded_notes = []
        self.rest_recording_mode = config_manager.get_config("rest_mode")
        self.last_record_time = 0.0

        from ui import Button
        self.buttons = [
            Button(lang_manager.translate("back"), 30, 30, 50, 50, on_back, font, 'back.png'),
            Button(lang_manager.translate("record"), 670, 30, 50, 50, self.toggle_recording, font, 'record.png'),
            Button(lang_manager.translate("settings"), 720, 30, 50, 50, self.on_settings_clicked, font, 'settings.png')
        ]

    def toggle_recording(self):
        self.recording = not self.recording
        if self.recording:
            self.record_start_time = time.time()
            self.recorded_notes = []
            self.last_record_time = 0.0
            print("🔴 Recording started")
            self.show_download_button = False  # 關閉錄音時隱藏下載按鈕
        else:
            print("⏹ Recording stopped")
            # 錄音結束時自動產生 MIDI 檔並顯示下載按鈕
            # midi_path = self.save_recorded_notes_to_midi()
            print(f"Wait for download btn click")
            self.show_download_button = True
            self.midi_download_path = None

    def on_settings_clicked(self):
        # 關閉錄音
        if self.recording:
            self.toggle_recording()
        # 跳轉到設定畫面
        self.on_settings()

    def save_recorded_notes_to_midi(self, filename=None):
        mid = mido.MidiFile()
        track = mido.MidiTrack()
        mid.tracks.append(track)
        tempo = mido.bpm2tempo(144)
        track.append(mido.MetaMessage('set_tempo', tempo=tempo))
        ticks_per_beat = mid.ticks_per_beat
        events = []
        
        last_tick = 0
        
        for rec in self.recorded_notes:
            if rec['key'] == 'rest':
                rest_ticks = int((rec['duration']) * ticks_per_beat)
                last_tick += rest_ticks
                continue
                
            # 加入這段處理 None 的代碼
            if rec['end'] is None:
                # 如果結束時間是 None，設定為開始時間 + 1秒
                rec['end'] = rec['start'] + 1.0
                rec['duration'] = 1.0
                
            start_tick = max(0, int(rec['start'] * ticks_per_beat))
            end_tick = max(start_tick, int(rec['end'] * ticks_per_beat))
            track.append(mido.Message('note_on', note=rec['note'], velocity=64, time=max(0, start_tick - last_tick)))
            track.append(mido.Message('note_off', note=rec['note'], velocity=64, time=max(0, end_tick - start_tick)))
            last_tick = end_tick
            
        if not filename:
            filename = f"record_{int(time.time())}.mid"
        midi_path = os.path.join(path_manager.base_path, filename)
        mid.save(midi_path)
        return midi_path


    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:
                self.shift_octave(-1)
            elif event.key == pygame.K_x:
                self.shift_octave(1)
            elif event.key == pygame.K_o:  # 新增: 按下 O 鍵打開檔案
                if hasattr(self, "midi_ready_to_open") and self.midi_ready_to_open:
                    self.open_midi_file()

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
                        rel_start = now - self.record_start_time
                        print(f"[DEBUG] 按下: key={k}, note={note}, time={now:.3f}s, rel_start={rel_start:.3f}s")
                        self.recorded_notes.append({
                            'key': k,
                            'note': note,
                            'start': rel_start,
                            'end': None,
                            'duration': None
                        })
            elif k in self.active_notes:
                self.fs.noteoff(0, self.active_notes[k][0])
                if self.recording:
                    rel_end = now - self.record_start_time
                    for rec in reversed(self.recorded_notes):
                        if rec['key'] == k and rec['end'] is None:
                            rec['end'] = rel_end
                            rec['duration'] = rec['end'] - rec['start']
                            print(f"[DEBUG] 放開: key={k}, note={note}, time={now:.3f}s, rel_end={rel_end:.3f}s")
                            print(f"[DEBUG] 當前所有recorded_notes: {self.recorded_notes}")
                            break

        for i, k in enumerate(BLACK_KEYS):
            note = self.base_note + BLACK_OFFSETS[i]
            if keys[getattr(pygame, f'K_{k}')]:
                new_active_notes[k] = note
                if k not in self.active_notes:
                    self.fs.noteon(0, note, 100)
                    if self.recording:
                        played_now.append(note)
                        rel_start = now - self.record_start_time
                        print(f"[DEBUG] 按下: key={k}, note={note}, time={now:.3f}s, rel_start={rel_start:.3f}s")
                        self.recorded_notes.append({
                            'key': k,
                            'note': note,
                            'start': rel_start,
                            'end': None,
                            'duration': None
                        })
            elif k in self.active_notes:
                self.fs.noteoff(0, self.active_notes[k][0])
                if self.recording:
                    rel_end = now - self.record_start_time
                    for rec in reversed(self.recorded_notes):
                        if rec['key'] == k and rec['end'] is None:
                            rec['end'] = rel_end
                            rec['duration'] = rec['end'] - rec['start']
                            print(f"[DEBUG] 放開: key={k}, note={note}, time={now:.3f}s, rel_end={rel_end:.3f}s")
                            print(f"[DEBUG] 當前所有recorded_notes: {self.recorded_notes}")
                            break

        # 自動補休止符
        if self.recording and self.rest_recording_mode:
            # 找出上一個 note 的結束時間
            last_end = 0.0
            for rec in reversed(self.recorded_notes):
                if rec['end'] is not None:
                    last_end = rec['end']
                    break
            # 如果目前沒有任何按鍵按下，且距離上一個 note 結束超過 1 秒
            if not new_active_notes and (now - self.record_start_time - last_end) > 1.0:
                rest_start = last_end
                rest_end = now - self.record_start_time
                print(f"[DEBUG] 休止: start={rest_start:.3f}s, end={rest_end:.3f}s, duration={rest_end - rest_start:.3f}s")
                self.recorded_notes.append({
                    'key': 'rest',
                    'note': None,
                    'start': rest_start,
                    'end': rest_end,
                    'duration': rest_end - rest_start
                })

        self.active_notes = {k: (note, now) for k, note in new_active_notes.items()}
        
    
    def shift_octave(self, direction):
        new_base = self.base_note + direction * 12
        if MIN_MIDI <= new_base <= MAX_MIDI - 12:
            self.base_note = new_base

    def midi_to_name(self, midi_num):
        names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        return f"{names[midi_num % 12]}{(midi_num // 12) - 1}"

    def draw(self, screen):
        from ui import Button
        screen.fill((255, 255, 255))
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        margin = 30
        
        if getattr(self, "notice_text", None):
            if time.time() - self.notice_start_time < self.notice_duration:
                box_rect = pygame.Rect(0, 0, screen.get_width(), 40)
                pygame.draw.rect(screen, (200, 255, 200), box_rect)
                pygame.draw.line(screen, (0, 180, 0), (0, 40), (screen.get_width(), 40), 2)

                notice = self.font.render(self.notice_text, True, (0, 100, 0))
                text_rect = notice.get_rect(center=(screen.get_width() // 2, 20))
                screen.blit(notice, text_rect)
            else:
                self.notice_text = None

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
        # 顯示下載按鈕（僅在錄音結束後，且在record/settings按鈕下方）
        if hasattr(self, 'show_download_button') and self.show_download_button:
            # 取得 record 與 settings 按鈕的 y 座標與高度
            record_btn = self.buttons[1]
            settings_btn = self.buttons[2]
            download_btn = Button(lang_manager.translate('downloadMidiBtn'), 700, 80, 50, 50, self.download_midi_file_and_notice(self.delayed_back, self.show_notice), self.font, 'download.png')
            download_btn.draw(screen)
            self.buttons.append(download_btn)
            # 顯示提示訊息
            if hasattr(self, 'download_message') and self.download_message:
                msg = self.font.render(self.download_message, True, (200, 50, 50))
                screen.blit(msg, (30, 180))

    def download_midi_file(self):
        if not self.midi_download_path:
            self.midi_download_path = self.save_recorded_notes_to_midi()
        print(f"[DEBUG] MIDI file saved to: {self.midi_download_path}")
        # 改為簡短提示，不顯示下載路徑
        self.download_message = lang_manager.translate("download_complete")
        self.midi_ready_to_open = True
        
        # 仍然保留按 O 開啟的提示
        self.download_message += lang_manager.translate("press_o_to_open")

    def show_notice(self, text, duration=1.5):
        print("show notice!")
        self.notice_text = text
        self.notice_start_time = time.time()
        self.notice_duration = duration
    def delayed_back(self, delay_seconds):
        self._return_after = time.time() + delay_seconds

    def download_midi_file_and_notice(self, original_callback, notify_text_fn=None):
        
        def callback():
            if notify_text_fn:
                notify_text_fn(lang_manager.translate("download_success"), duration=1.5)
            self.download_midi_file()
            original_callback(1.5)
            print("[DEBUG] download_midi_file_and_notice BUTTON callback triggered")
            print("[DEBUG] download_midi_file CALLED")
        
        return callback

    def open_midi_file(self):
        """使用預設應用程式開啟 MIDI 檔案"""
        if not hasattr(self, "midi_download_path") or not self.midi_download_path:
            return
            
        try:
            # 根據不同作業系統使用不同命令開啟檔案
            import platform
            system = platform.system()
            
            if system == 'Windows':
                import os
                os.startfile(self.midi_download_path)
                success = True
            elif system == 'Darwin':  # macOS
                ret = os.system(f'open "{self.midi_download_path}"')
                success = (ret == 0)
            else:  # Linux 或其他
                ret = os.system(f'xdg-open "{self.midi_download_path}"')
                success = (ret == 0)
                
            if success:
                self.show_notice(lang_manager.translate("midi_opened"))
            else:
                self.show_notice(lang_manager.translate("cannot_open_file"))
                    
        except Exception as e:
            print(f"開啟檔案時發生錯誤: {e}")
            self.show_notice(lang_manager.translate("error_opening_file"))
