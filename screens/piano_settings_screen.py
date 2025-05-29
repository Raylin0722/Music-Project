import pygame
import lang_manager
import config_manager
from ui import Button, Slider
import time
from screens.screen_base import Screen

class PianoSettingsScreen(Screen):
    def toggle_rest_mode(self):
        self.current_mode = not self.current_mode
        self.rest_button.text = lang_manager.translate("rest_mode_on") if self.current_mode else lang_manager.translate("rest_mode_off")

    def __init__(self, font, on_back):
        super().__init__()
        self.font = font
        self.on_back = on_back
        self.current_mode=False
        self.buttons = []
        self.volume_slider = Slider(60, 100, 300, 0,100, config_manager.get_config("volume"),)
        self.rest_button = Button(lang_manager.translate("rest_mode_on") if config_manager.get_config("rest_mode") else lang_manager.translate("rest_mode_off"), 100, 160, 120, 30, self.toggle_rest_mode, font)
        self.buttons.append(self.rest_button)

        self.instructions = [
            lang_manager.translate("hint_zx_switch"),
            lang_manager.translate("hint_keys_note"),
            lang_manager.translate("hint_click_record")
        ]
        self.back_btn = Button( lang_manager.translate("back"), 30, 30, 50, 50, config_manager.make_auto_save_back_piano(self.delayed_back, self.volume_slider, self.current_mode, self.show_notice), font, 'back.png')
        self.buttons.append(self.back_btn)

    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)
        self.volume_slider.handle_event(event)
        

    def update(self, dt):
        if hasattr(self, "_return_after") and self._return_after:
            if time.time() >= self._return_after:
                self._return_after = None
                self.on_back()
        

    def draw(self, screen):
        screen.fill((240, 240, 240))
        center_x = screen.get_width() // 2
        y = 60

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

        # 標題
        title = self.font.render(lang_manager.translate("settings"), True, (0, 0, 0))
        screen.blit(title, (center_x - title.get_width() // 2, y))
        y += 60
        
        self.back_btn.rect.topleft = (30, 30)
        self.back_btn.draw(screen)

        # 音量顯示 + 滑桿
        volume_val = int(self.volume_slider.get_value())
        volume_text = self.font.render(f"{lang_manager.translate('volume')}: {volume_val}%", True, (0, 0, 0))
        screen.blit(volume_text, (center_x - volume_text.get_width() // 2, y))
        y += 40

        self.volume_slider.rect.centerx = center_x
        self.volume_slider.rect.y = y+20
        self.volume_slider.draw(screen)
        y += 80

        # 自動休止符開關
        rest_text = self.font.render(lang_manager.translate("auto_rest"), True, (0, 0, 0))
        total_width = rest_text.get_width() + 20 + self.rest_button.rect.width
        start_x = center_x - total_width // 2
        screen.blit(rest_text, (start_x, y - 15))
        self.rest_button.rect.topleft = (start_x + rest_text.get_width() + 20, y)
        self.rest_button.draw(screen)
        y += 60

        # 使用說明標題
        help_title = self.font.render(lang_manager.translate("instructions"), True, (0, 0, 0))
        screen.blit(help_title, (center_x - help_title.get_width() // 2, y))
        y += 40

        # 使用說明每行文字
        cnt=1; maxWidth=0
        for line in self.instructions:
            txt = self.font.render(f"{cnt}. {line}", True, (100, 100, 100))
            maxWidth = max(maxWidth, txt.get_width())
            
        for line in self.instructions:
            txt = self.font.render(f"{cnt}. {line}", True, (100, 100, 100))
            screen.blit(txt, (center_x - maxWidth // 2, y))
            y += 40
            cnt+=1
            
    def show_notice(self, text, duration=1.5):
        print("show notice!")
        self.notice_text = text
        self.notice_start_time = time.time()
        self.notice_duration = duration
    def delayed_back(self, delay_seconds):
        self._return_after = time.time() + delay_seconds

        