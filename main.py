# main.py - 使用畫面類別管理的主程式架構

import pygame
import sys
from font_manager import FontManager
import lang_manager
from screens.start_screen import StartScreen

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mood Composer")
clock = pygame.time.Clock()

# 初始化字型管理與畫面狀態
font = FontManager()
current_screen = None

# 畫面切換邏輯
def switch_to_start():
    global current_screen
    current_screen = StartScreen(
        font.get(lang_manager.LANGUAGE),
        switch_to_input,
        switch_to_settings,
        set_language_and_refresh
    )

def switch_to_input():
    print("切換至輸入畫面（待擴充）")

# 當語言切換後要重建畫面
def set_language_and_refresh():
    print("當前的LANGUAGE為: ", lang_manager.LANGUAGE)
    lang_manager.set_language()
    switch_to_start()
    print("語言已切換至: ", lang_manager.LANGUAGE)
    
    
def switch_to_settings():
    print("切換至設定畫面（待擴充）")

# 啟動第一個畫面
switch_to_start()

# 主迴圈
running = True
while running:
    screen.fill((240, 240, 240))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            current_screen.handle_event(event)

    current_screen.update(0)
    current_screen.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
