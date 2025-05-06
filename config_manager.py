# config_manager.py
import json
import os

CONFIG_FILE = "config.json"

default_config = {
    "volume": 50,
    "save_path": "./output"
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
