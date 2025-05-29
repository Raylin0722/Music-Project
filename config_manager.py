# config_manager.py
import json
import os
from path_manager import path_manager

CONFIG_FILE = path_manager.get_path("base", "config.json")
print("[DEBUG] CONFIG_FILE =", CONFIG_FILE)
default_config = {
    "volume": 50,
    "save_path": "./output",
    "width": 800,
    "height": 600,
    "fullscreen": False,
    "rest_mode": True
}

current_config = default_config.copy()

def load_config():
    global current_config
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            current_config = json.load(f)

def save_config():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(current_config, f, indent=2)

def apply_config():
    import pygame
    pygame.mixer.music.set_volume(current_config["volume"] / 100)

def set_config(key, value):
    current_config[key] = value

def get_config(key):
    return current_config.get(key, default_config[key])

def make_auto_save_back(original_callback, slider, textinput, notify_text_fn=None):
    print("[DEBUG] make_auto_save_back CALLED")
    def callback():
        print("[DEBUG] auto-save BUTTON callback triggered")
        set_config("volume", slider.get_value())
        set_config("save_path", textinput.get_text())
        save_config()
        if notify_text_fn:
            notify_text_fn("Settings saved successfully!", duration=1.5)
        original_callback(1.5)
    print("Auto save complete!")
    print("[DEBUG] notify_text_fn =", notify_text_fn)
    return callback

def make_auto_save_back_piano(original_callback, slider, auto_reset, notify_text_fn=None):
    print("[DEBUG] make_auto_save_back_piano CALLED")
    def callback():
        print("[DEBUG] auto-save BUTTON callback triggered")
        set_config("volume", slider.get_value())
        set_config("auto_reset", auto_reset)
        save_config()
        if notify_text_fn:
            notify_text_fn("Settings saved successfully!", duration=1.5)
        original_callback(1.5)
    print("Auto save complete!")
    print("[DEBUG] notify_text_fn =", notify_text_fn)
    return callback

def make_config_save_file():
    save_config()