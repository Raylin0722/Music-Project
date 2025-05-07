# screens/settings_screen.py

import pygame
from screens.screen_base import Screen
from ui import Button, Slider, TextInput
import lang_manager
import config_manager
import time

class SettingsScreen(Screen):
    def __init__(self, font, on_back):
        super().__init__()
        self.font = font
        self.on_back = on_back
        self.volume_slider = Slider(300, 200, 400, 0, 100, config_manager.get_config("volume"))
        self.path_input = TextInput(300, 300, 400, font,config_manager.get_config("save_path"))
        self.path_input.active = True
        self.buttons = [
            Button(lang_manager.translate("back"), 300, 400, 200, 50, config_manager.make_auto_save_back(self.delayed_back, self.volume_slider, self.path_input, self.show_notice), font)
        ]
        
    def handle_event(self, event):

        self.volume_slider.handle_event(event)
        self.path_input.handle_event(event)  # 暫時註解這一行

        for b in self.buttons:
            b.handle_event(event)
    def update(self, dt):
        if hasattr(self, "_return_after") and self._return_after:
            if time.time() >= self._return_after:
                self._return_after = None
                self.on_back()

    def draw(self, screen):
        screen.fill((220, 220, 220))


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



        y = 100
        center_x = screen.get_width() // 2

        # 標題
        title = self.font.render(lang_manager.translate("settings"), True, (0, 0, 0))
        screen.blit(title, (center_x - title.get_width() // 2, y))
        y += 80

        # 音量文字
        volume_text = self.font.render(f"{lang_manager.translate('volume')}: {self.volume_slider.get_value()}%", True, (0, 0, 0))
        screen.blit(volume_text, (center_x - volume_text.get_width() // 2, y))
        y += 60

        # 音量滑桿
        self.volume_slider.rect.centerx = screen.get_width() // 2
        self.volume_slider.rect.y = y
        self.volume_slider.draw(screen)
        y += 60

        # 存檔路徑文字
        path_text = self.font.render(lang_manager.translate("save_path"), True, (0, 0, 0))
        screen.blit(path_text, (center_x - path_text.get_width() // 2, y))
        y += 60

        # 路徑輸入框
        self.path_input.rect.centerx = screen.get_width() // 2
        self.path_input.rect.y = y
        self.path_input.draw(screen)
        y += 80

        # 返回按鈕
        for b in self.buttons:
            b.rect.topleft = (center_x - b.rect.width // 2, y)
            b.draw(screen)
        


    def get_settings(self):
        return {
            "volume": self.volume_slider.get_value(),
            "save_path": self.path_input.get_text()
        }
    def show_notice(self, text, duration=1.5):
        print("show notice!")
        self.notice_text = text
        self.notice_start_time = time.time()
        self.notice_duration = duration
    def delayed_back(self, delay_seconds):
        self._return_after = time.time() + delay_seconds
