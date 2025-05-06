# screens/settings_screen.py

import pygame
from screens.screen_base import Screen
from ui import Button, Slider, TextInput
import lang_manager
import config_manager

class SettingsScreen(Screen):
    def __init__(self, font, on_back):
        super().__init__()
        self.font = font
        self.on_back = on_back

        self.volume_slider = Slider(300, 200, 200, 0, 100, 50)
        self.path_input = TextInput(300, 300, 300, font)

        self.buttons = [
            Button(lang_manager.translate("back"), 300, 400, 200, 50, on_back, font)
        ]

    def handle_event(self, event):
        self.volume_slider.handle_event(event)
        self.path_input.handle_event(event)
        for b in self.buttons:
            b.handle_event(event)   

    def update(self, dt):
        pass  # 若有動畫效果可處理

    def draw(self, screen):
        screen.fill((220, 220, 220))

        y = 100
        center_x = screen.get_width() // 2

        # 標題
        title = self.font.render(lang_manager.translate("settings"), True, (0, 0, 0))
        screen.blit(title, (center_x - title.get_width() // 2, y))
        y += 80

        # 音量文字
        volume_text = self.font.render(f"{lang_manager.translate('volume')}: {self.volume_slider.get_value()}%", True, (0, 0, 0))
        screen.blit(volume_text, (300, y))
        y += 60

        # 音量滑桿
        self.volume_slider.rect.topleft = (300, y)
        self.volume_slider.draw(screen)
        y += 60

        # 存檔路徑文字
        path_text = self.font.render(lang_manager.translate("save_path"), True, (0, 0, 0))
        screen.blit(path_text, (300, y))
        y += 60

        # 路徑輸入框
        self.path_input.rect.topleft = (300, y)
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
