import pygame
import os
import music21
from screens.screen_base import Screen
import lang_manager
from config_manager import get_config
import subprocess
import re

def get_unique_filename(folder, base_name, ext):
    """
    自動產生不重複的檔名，如 score.mid、score (1).mid、score (2).mid ...
    """
    filename = f"{base_name}.{ext}"
    path = os.path.join(folder, filename)
    if not os.path.exists(path):
        return path
    # 若已存在，依序加 (1)、(2)...
    i = 1
    while True:
        filename = f"{base_name} ({i}).{ext}"
        path = os.path.join(folder, filename)
        if not os.path.exists(path):
            return path
        i += 1

class MidiEditorScreen(Screen):
    def __init__(self, font, on_finish):
        super().__init__()
        self.font = font
        self.on_finish = on_finish
        self.node_area_rect = pygame.Rect(50, 210, 700, 300)

        # 常用樂器清單
        self.instruments = [
            "piano", "acoustic guitar", "electric guitar", "violin", "cello", "contrabass", "flute", "clarinet",
            "trumpet", "trombone", "saxophone", "drums", "harp", "organ", "voice"
        ]

        # 初始音軌資料
        self.tracks = [
            {
                "name": "Track 1",
                "instrument": "piano",
                "notes": []
            }
        ]
        self.current_track_index = 0
        self.selected_note_index = None

        # 樂譜圖片
        self.score_image_surface = None
        # 拖曳狀態
        self.image_offset = [0, 0]
        self.dragging = False
        self.drag_start = (0, 0)
        self.image_offset_start = (0, 0)
        # 圖片縮放比例
        self.image_scale = 1.0
        self.base_scale = 1.0  # 基準縮放倍率

        # 樂譜圖片顯示開關
        self.show_score_image = True

        # 樂器輸入模式
        self.input_mode = None
        self.input_text = ""
        self.show_help = False  # 是否顯示操作說明

        # help 視窗滾動
        self.help_offset = 0
        self.help_dragging = False
        self.help_drag_start = 0
        self.help_offset_start = 0

        # 音符區域拖曳
        self.node_offset = 0
        self.node_dragging = False
        self.node_drag_start = 0
        self.node_offset_start = 0

    # --- 新增：確保選定 node 可見 ---
    def ensure_selected_node_visible(self):
        if self.selected_note_index is None:
            return
        
        # 關鍵：這裡要使用與draw中完全相同的計算方式
        line_height = 36
        area_height = self.node_area_rect.height
        buffer_space = 12  # 加大緩衝空間，確保看得到選中區域
        
        # 關鍵修正：這裡計算方式錯誤，正確的做法是不要加上offset
        item_y = self.selected_note_index * line_height  # 選中項在內容中的絕對位置
        visible_top = -self.node_offset  # 當前可見區域的頂部位置
        visible_bottom = visible_top + area_height  # 當前可見區域的底部位置
        
        # 如果在可見區域外，則移動捲軸
        if item_y < visible_top + buffer_space:
            # 向下捲動，顯示頂部項
            self.node_offset = -item_y + buffer_space
        elif item_y + line_height > visible_bottom - buffer_space:
            # 向上捲動，顯示底部項
            self.node_offset = -(item_y + line_height - area_height + buffer_space)
        
        # 與draw中保持相同的限制計算
        notes = self.tracks[self.current_track_index]["notes"]
        bottom_buffer = 12
        content_height = len(notes) * line_height + bottom_buffer
        extra_scroll_room = 20
        min_offset = min(0, area_height - content_height - extra_scroll_room)
        max_offset = 0
        
        # 套用限制
        self.node_offset = max(min(self.node_offset, max_offset), min_offset)

    def add_note(self):
        notes = self.tracks[self.current_track_index]["notes"]
        if notes:
            last_note = notes[-1]
            new_start = last_note["start"] + last_note["duration"]
        else:
            new_start = 0.0
        notes.append({
            "pitch": 60,
            "start": new_start,
            "duration": 1.0
        })
        self.selected_note_index = len(notes) - 1
        self.ensure_selected_node_visible()

    def add_track(self):
        track_num = len(self.tracks) + 1
        self.tracks.append({
            "name": f"Track {track_num}",
            "instrument": "piano",
            "notes": []
        })
        self.current_track_index = len(self.tracks) - 1
        self.selected_note_index = None

    def prev_track(self):
        self.current_track_index = max(0, self.current_track_index - 1)
        self.selected_note_index = None

    def next_track(self):
        self.current_track_index = min(len(self.tracks) - 1, self.current_track_index + 1)
        self.selected_note_index = None

    def switch_instrument(self):
        track = self.tracks[self.current_track_index]
        current = track["instrument"]
        idx = self.instruments.index(current) if current in self.instruments else 0
        idx = (idx + 1) % len(self.instruments)
        track["instrument"] = self.instruments[idx]

    def start_instrument_input(self):
        self.input_mode = "instrument"
        self.input_text = ""

    def handle_event(self, event):
        notes = self.tracks[self.current_track_index]["notes"]
        # help 視窗滾動與關閉
        if self.show_help:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_h, pygame.K_ESCAPE):
                    self.show_help = False
                    self.help_offset = 0
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.help_dragging = True
                    self.help_drag_start = event.pos[1]
                    self.help_offset_start = self.help_offset
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.help_dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if self.help_dragging:
                    dy = event.pos[1] - self.help_drag_start
                    self.help_offset = self.help_offset_start + dy
            elif event.type == pygame.MOUSEWHEEL:
                self.help_offset += event.y * -40
            return

        if self.input_mode == "instrument":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # 支援數字代號與英文名稱
                    input_str = self.input_text.strip()
                    if input_str.isdigit():
                        idx = int(input_str) - 1
                        if 0 <= idx < len(self.instruments):
                            self.tracks[self.current_track_index]["instrument"] = self.instruments[idx]
                    else:
                        try:
                            music21.instrument.fromString(input_str)
                            self.tracks[self.current_track_index]["instrument"] = input_str
                        except Exception:
                            pass  # 可加提示
                    self.input_mode = None
                elif event.key == pygame.K_ESCAPE:
                    self.input_mode = None
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                else:
                    if event.unicode.isprintable():
                        self.input_text += event.unicode
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:
                self.show_help = not self.show_help
            elif event.key == pygame.K_SPACE:
                self.show_score_image = not self.show_score_image
            # --- 新增：刪除 node ---
            elif event.key in (pygame.K_DELETE, pygame.K_BACKSPACE):
                if notes and self.selected_note_index is not None:
                    notes.pop(self.selected_note_index)
                    # 調整選取索引
                    if self.selected_note_index >= len(notes):
                        self.selected_note_index = len(notes) - 1
                    if len(notes) == 0:
                        self.selected_note_index = None
                    self.ensure_selected_node_visible()
            elif event.key == pygame.K_LEFT:
                if notes:
                    if self.selected_note_index is None:
                        self.selected_note_index = 0
                    else:
                        self.selected_note_index = max(0, self.selected_note_index - 1)
                    self.ensure_selected_node_visible()
            elif event.key == pygame.K_RIGHT:
                if notes:
                    if self.selected_note_index is None:
                        self.selected_note_index = 0
                    else:
                        self.selected_note_index = min(len(notes) - 1, self.selected_note_index + 1)
                    self.ensure_selected_node_visible()
            elif event.key == pygame.K_a:
                self.add_note()
            elif event.key == pygame.K_t:
                self.add_track()
            elif event.key == pygame.K_UP:
                self.prev_track()
            elif event.key == pygame.K_DOWN:
                self.next_track()
            elif event.key == pygame.K_w:
                if notes and self.selected_note_index is not None:
                    notes[self.selected_note_index]["pitch"] += 1
            elif event.key == pygame.K_s:
                if notes and self.selected_note_index is not None:
                    notes[self.selected_note_index]["pitch"] -= 1
            elif event.key == pygame.K_q:
                if notes and self.selected_note_index is not None:
                    notes[self.selected_note_index]["duration"] = max(0.125, notes[self.selected_note_index]["duration"] - 0.125)
            elif event.key == pygame.K_e:
                if notes and self.selected_note_index is not None:
                    notes[self.selected_note_index]["duration"] += 0.125
            elif event.key == pygame.K_z:
                if notes and self.selected_note_index is not None:
                    notes[self.selected_note_index]["start"] = max(0.0, notes[self.selected_note_index]["start"] - 0.25)
            elif event.key == pygame.K_x:
                if notes and self.selected_note_index is not None:
                    notes[self.selected_note_index]["start"] += 0.25
            elif event.key == pygame.K_i:
                self.switch_instrument()
            elif event.key == pygame.K_l:
                self.start_instrument_input()
            elif event.key == pygame.K_RETURN:
                self.generate_score_image()
            elif event.key == pygame.K_o:
                # 只有已產生圖片時才允許
                if self.score_image_surface:
                    self.generate_score_image()  # 先更新圖片
                    save_path = get_config("save_path")
                    if not os.path.exists(save_path):
                        os.makedirs(save_path)
                    midi_path = get_unique_filename(save_path, "score", "mid")
                    self.export_to_midi(midi_path)
            elif event.key == pygame.K_ESCAPE:
                self.on_finish()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.score_image_surface and self.show_score_image:
                mx, my = event.pos
                # 置中顯示，計算顯示區域
                view_w = 700
                view_h = 320
                screen_w = pygame.display.get_surface().get_width()
                screen_h = pygame.display.get_surface().get_height()
                show_x = (screen_w - view_w) // 2
                show_y = (screen_h - view_h) // 2
                if show_x <= mx <= show_x + view_w and show_y <= my <= show_y + view_h:
                    self.dragging = True
                    self.drag_start = (mx, my)
                    self.image_offset_start = self.image_offset.copy()
            # 判斷是否點在 node 區塊
            node_area = self.node_area_rect
            if node_area.collidepoint(event.pos):
                self.node_dragging = True
                self.node_drag_start = event.pos[1]
                self.node_offset_start = self.node_offset

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
                self.node_dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                dx = event.pos[0] - self.drag_start[0]
                dy = event.pos[1] - self.drag_start[1]
                self.image_offset[0] = self.image_offset_start[0] + dx
                self.image_offset[1] = self.image_offset_start[1] + dy
            if self.node_dragging:
                dy = event.pos[1] - self.node_drag_start
                self.node_offset = self.node_offset_start + dy
                content_height = len(notes) * 36
                area_height = self.node_area_rect.height
                extra_scroll_room = 20  # 加上這個
                min_offset = min(0, area_height - content_height - extra_scroll_room)
                max_offset = 0
                self.node_offset = max(min(self.node_offset, max_offset), min_offset)

        elif event.type == pygame.MOUSEWHEEL:
            # 滾輪上放大，下縮小，限制範圍
            if event.y > 0:
                self.image_scale = min(self.image_scale + 0.1, 3.0)
            elif event.y < 0:
                self.image_scale = max(self.image_scale - 0.1, 1.0)  # 最小為1.0
            # 滾輪控制 node 區塊捲動
            node_area = self.node_area_rect
            mx, my = pygame.mouse.get_pos()
            if node_area.collidepoint((mx, my)):
                self.node_offset += event.y * -36
                content_height = len(notes) * 36
                area_height = self.node_area_rect.height - 10
                extra_scroll_room = 20  # 加上這個
                min_offset = min(0, area_height - content_height - extra_scroll_room)
                max_offset = 0
                self.node_offset = max(min(self.node_offset, max_offset), min_offset)

    def update(self, dt):
        pass

    def export_to_midi(self, midi_path):
        score = music21.stream.Score()
        for t in self.tracks:
            part = music21.stream.Part()
            part.partName = t["name"]
            try:
                part.insert(0, music21.instrument.fromString(t["instrument"]))
            except Exception:
                pass
            sorted_notes = sorted(t["notes"], key=lambda n: n["start"])
            for n in sorted_notes:
                note = music21.note.Note(n["pitch"])
                note.quarterLength = n["duration"]
                note.offset = n["start"]
                part.append(note)
            score.append(part)
        score.write('midi', fp=midi_path)

    def export_to_musicxml(self):
        # 確保 tmp 資料夾存在
        if not os.path.exists("tmp"):
            os.makedirs("tmp")
        xml_path = os.path.join("tmp", "score.musicxml")
        score = music21.stream.Score()
        for t in self.tracks:
            part = music21.stream.Part()
            part.partName = t["name"]
            try:
                part.insert(0, music21.instrument.fromString(t["instrument"]))
            except Exception:
                pass
            # 依 start 排序，避免 music21 自動補休止符
            sorted_notes = sorted(t["notes"], key=lambda n: n["start"])
            for n in sorted_notes:
                note = music21.note.Note(n["pitch"])
                note.quarterLength = n["duration"]
                note.offset = n["start"]
                part.append(note)
            score.append(part)
        score.write('musicxml', fp=xml_path)
        return xml_path

    def generate_score_image(self):
        xml_path = self.export_to_musicxml()
        png_path = os.path.join("tmp", "score.png")
        musescore_path = r"MuseScorePortable\App\MuseScore\bin\MuseScore4.exe"  # 請依你的安裝路徑調整
        subprocess.run([musescore_path, xml_path, "-o", png_path])
        # 處理 MuseScore 可能產生 score-1.png 的情況
        png1_path = os.path.join("tmp", "score-1.png")
        if os.path.exists(png1_path):
            self.score_image_surface = pygame.image.load(png1_path)
        elif os.path.exists(png_path):
            self.score_image_surface = pygame.image.load(png_path)
        else:
            self.score_image_surface = None

        if self.score_image_surface:
            view_w = 700
            view_h = 320
            orig_w, orig_h = self.score_image_surface.get_width(), self.score_image_surface.get_height()
            self.base_scale = view_w / orig_w
            self.image_scale = 1.0
            self.image_offset = [0, 0]

    def draw(self, screen):
        screen.fill((245, 245, 245))

        # 標題
        title = self.font.render(lang_manager.translate("midi_editor"), True, (0, 0, 0))
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 20))

        # 樂器輸入模式時不顯示 now_editing，改顯示輸入框
        if self.input_mode == "instrument":
            input_surface = self.font.render(
                f"Instrument: {self.input_text}_", True, (200, 80, 80))
            x = (screen.get_width() - input_surface.get_width()) // 2
            screen.blit(input_surface, (x, 80))
        else:
            track_info = self.tracks[self.current_track_index]
            track_label = self.font.render(
                f"{lang_manager.translate('now_editing')}{track_info['name']}({track_info['instrument']})",
                True, (50, 50, 50))
            screen.blit(track_label, (50, 80))

            note_preview = self.font.render(
                f"{lang_manager.translate('current_nodes_num')}" + str(len(track_info['notes'])),
                True, (80, 80, 80))
            screen.blit(note_preview, (50, 140))

            # --- 新增：node 區塊裁切與偏移 ---
            node_area = self.node_area_rect
            line_height = 36
            # 增加底部緩衝區，原本只加1行，現在加1.5行或2行的高度
            bottom_buffer = 12 # 或 line_height * 2 更多緩衝
            content_height = len(track_info["notes"]) * line_height + bottom_buffer
            node_surface = pygame.Surface((node_area.width, max(1, content_height)))
            node_surface.fill((235, 235, 245))

            y = 0
            for idx, note in enumerate(track_info["notes"]):
                color = (200, 40, 40) if idx == self.selected_note_index else (60, 60, 120)
                note_text = f"{idx+1}. pitch: {note['pitch']}, start: {note['start']}, duration: {note['duration']}"
                note_surface = self.font.render(note_text, True, color)
                node_surface.blit(note_surface, (10, y))
                y += line_height

            # 限制 node_offset
            line_height = 36
            area_height = node_area.height
            content_height = len(track_info["notes"]) * line_height + bottom_buffer
            # 這裡加上額外的捲動空間，讓捲軸能拉得更下面
            extra_scroll_room = 20  # 你可以調整這個值，越大捲動範圍越大
            min_offset = min(0, area_height - content_height - extra_scroll_room)
            max_offset = 0
            self.node_offset = max(min(self.node_offset, max_offset), min_offset)

            screen.blit(
                node_surface,
                (node_area.x, node_area.y),
                area=pygame.Rect(0, -self.node_offset, node_area.width, node_area.height)
            )
        help_hint = lang_manager.translate("show_help_hint")
        help_short = self.font.render(help_hint, True, (120, 120, 120))
        # 只有在未顯示 help 視窗時才顯示提示
        if not self.show_help:
            screen.blit(help_short, (40, 540))  # 原本是560，改成540


        # 全螢幕覆蓋 help
        if self.show_help:
            margin = 40
            overlay_rect = pygame.Rect(margin, margin, screen.get_width() - margin * 2, screen.get_height() - margin * 2)
            overlay = pygame.Surface((overlay_rect.width, overlay_rect.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (overlay_rect.x, overlay_rect.y))

            # 取得標題
            help_title = lang_manager.translate("help_title")
            instr_title = lang_manager.translate("instrument_list_title")
            help_text = lang_manager.translate("help_midi_editor")

            # 分割操作說明與樂器表
            if "\n\nInstrument List:" in help_text:
                help_part, instr_part = help_text.split("\n\nInstrument List:", 1)
                instr_part = instr_part.strip()
            elif "\n\n樂器對照表：" in help_text:
                help_part, instr_part = help_text.split("\n\n樂器對照表：", 1)
                instr_part = instr_part.strip()
            else:
                help_part = help_text
                instr_part = ""

            # 操作說明自動換行
            max_pixel_width = overlay_rect.width - 40  # 內容區寬度
            def wrap_lines(text):
                words = text.split()
                lines = []
                current = ""
                for word in words:
                    test_line = current + (" " if current else "") + word
                    if self.font.size(test_line)[0] > max_pixel_width:
                        lines.append(current)
                        current = word
                    else:
                        current = test_line
                if current:
                    lines.append(current)
                return lines

            help_lines = wrap_lines(help_part)

            # 行高
            line_height = 34
            title_height = 48

            # 處理 instr_lines，將過長的行自動換行
            def wrap_instr_lines(instr_lines, max_pixel_width):
                wrapped = []
                for line in instr_lines:
                    if self.font.size(line)[0] <= max_pixel_width:
                        wrapped.append(line)
                    else:
                        words = line.split()
                        current = ""
                        for word in words:
                            test_line = current + (" " if current else "") + word
                            if self.font.size(test_line)[0] > max_pixel_width:
                                wrapped.append(current)
                                current = word
                            else:
                                current = test_line
                        if current:
                            wrapped.append(current)
                return wrapped

            # 先將 instr_part 拆成行，再傳給 wrap_instr_lines
            instr_lines_raw = [line.strip() for line in instr_part.splitlines() if line.strip()]

            # 處理最後一句 Use...，分解成三點
            if instr_lines_raw and instr_lines_raw[-1].startswith("Use I"):
                instr_lines_raw = instr_lines_raw[:-1]
                instr_lines_raw += [
                    lang_manager.translate("cycle_ionstrucment"), 
                    lang_manager.translate("enter_instrucment"),
                    lang_manager.translate("comfirm_instructment"),
                    lang_manager.translate("toggle_score_hint")
                ]

            instr_lines = wrap_instr_lines(instr_lines_raw, max_pixel_width)

            # 合併所有要顯示的行（含標題）
            display_lines = []
            display_lines.append(("title", help_title))
            display_lines += [("bullet", l) for l in help_lines]
            display_lines.append(("gap", ""))  # 空行
            display_lines.append(("title", instr_title))
            display_lines += [("bullet", l) for l in instr_lines]

            # 計算內容高度
            total_height = 0
            for kind, _ in display_lines:
                total_height += title_height if kind == "title" else line_height

            # 限制 help_offset
            view_height = overlay_rect.height
            min_offset = min(0, view_height - total_height - 40)
            max_offset = 0
            self.help_offset = max(min(self.help_offset, max_offset), min_offset)
            start_y = overlay_rect.y + 40 + self.help_offset

            # 顯示內容
            y = start_y
            for kind, line in display_lines:
                if kind == "title":
                    surf = self.font.render(line, True, (255, 255, 0))
                    x = overlay_rect.x + (overlay_rect.width - surf.get_width()) // 2
                    screen.blit(surf, (x, y))
                    y += title_height
                elif kind == "gap":
                    y += line_height // 2
                elif kind == "bullet":
                    bullet_line = f"• {line}"
                    surf = self.font.render(bullet_line, True, (255, 255, 255))
                    x = overlay_rect.x + 20
                    screen.blit(surf, (x, y))
                    y += line_height

        # 若已產生樂譜圖片，寬度等比縮放，高度可拖曳，支援縮放
        if self.score_image_surface and not self.show_help and self.show_score_image:
            img = self.score_image_surface
            view_w = 700
            view_h = 320

            orig_w, orig_h = img.get_width(), img.get_height()
            scale = self.base_scale * self.image_scale
            scaled_w = int(orig_w * scale)
            scaled_h = int(orig_h * scale)
            img_scaled = pygame.transform.smoothscale(img, (scaled_w, scaled_h))

            # 拖曳範圍（offset為負值時才會往右/下移動）
            max_x = max(0, scaled_w - view_w)
            max_y = max(0, scaled_h - view_h)
            self.image_offset[0] = max(min(self.image_offset[0], 0), -max_x)
            self.image_offset[1] = max(min(self.image_offset[1], 0), -max_y)

            # 置中顯示
            screen_w = screen.get_width()
            screen_h = screen.get_height()
            show_x = (screen_w - view_w) // 2
            show_y = (screen_h - view_h) // 2

            # 設定裁切區域
            area = pygame.Rect(-self.image_offset[0], -self.image_offset[1], view_w, view_h)
            screen.blit(img_scaled, (show_x, show_y), area)


