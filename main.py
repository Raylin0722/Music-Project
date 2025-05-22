import pygame
import sys
from font_manager import FontManager
import lang_manager
from screens.start_screen import StartScreen
from screens.settings_screen import SettingsScreen
from screens.input_screen import InputScreen
from screens.midi_load_screen import MidiLoadScreen
#from screens.midi_composer_screen import MidiComposerScreen
from screens.piano_settings_screen import PianoSettingsScreen
from screens.piano_screen import PianoScreen
import config_manager


pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mood Composer")
clock = pygame.time.Clock()

# 初始化字型管理與畫面狀態
font = FontManager()
current_screen = None
screens_cache = {
    "start": None,
    "settings": None,
    "input": None,
    "midi": None,
    "piano": None,
    "composer": None,
    "piano_settings": None
}
def switch_to_start():
    global current_screen
    if not screens_cache["start"]:
        screens_cache["start"] = StartScreen(
            font.get(lang_manager.LANGUAGE),
            switch_to_input,
            switch_to_settings,
            set_language_and_refresh
        )
    current_screen = screens_cache["start"]

def switch_to_input():
    global current_screen
    if not screens_cache["input"]:
        screens_cache["input"] = InputScreen(
            font.get(lang_manager.LANGUAGE),
            switch_to_midi_load,
            switch_to_piano,
            switch_to_mood,
            switch_to_composer,
            switch_to_start
        )
    current_screen = screens_cache["input"]

def switch_to_settings():
    global current_screen
    if not screens_cache["settings"]:
        screens_cache["settings"] = SettingsScreen(
            font.get(lang_manager.LANGUAGE),
            switch_to_start
        )
    current_screen = screens_cache["settings"]

def set_language_and_refresh():
    lang_manager.set_language()
    for k in screens_cache:
        screens_cache[k] = None
    
    switch_to_start()

def switch_to_midi_load():
    global current_screen
    if not screens_cache["midi"]:
        screens_cache["midi"] = MidiLoadScreen(
            font.get(lang_manager.LANGUAGE),
            switch_to_composer,
            switch_to_input
        )
    current_screen = screens_cache["midi"]


def switch_to_piano():
    global current_screen
    if not screens_cache["piano"]:
        screens_cache["piano"] = PianoScreen(
            font.get(lang_manager.LANGUAGE),
            switch_to_input,            
            switch_to_piano_settings
        )
    current_screen = screens_cache["piano"]
def switch_to_piano_settings():
    global current_screen
    if not screens_cache["piano_settings"]:
        screens_cache["piano_settings"] = PianoSettingsScreen(
            font.get(lang_manager.LANGUAGE),
            switch_to_piano,        # 返回 piano 畫面
        )
    current_screen = screens_cache["piano_settings"]

def switch_to_composer(midi_path):
    # global current_screen
    # screens_cache["composer"] = MidiComposerScreen(
    #     font.get(lang_manager.LANGUAGE),
    #     midi_path,
    #     switch_to_input
    # )
    # current_screen = screens_cache["composer"]
    pass
def switch_to_mood():
    pass


# 啟動第一個畫面
config_manager.load_config()
switch_to_start()

# 主迴圈
running = True
while running:
    
    screen.fill((240, 240, 240))

    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            running = False
            config_manager.make_config_save_file()
        else:
            current_screen.handle_event(event)

    current_screen.update(0)
    current_screen.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
