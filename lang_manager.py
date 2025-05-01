import json
import pygame

def load_language(lang_code):
    with open(f"assets/lang/{lang_code}.json", encoding="utf-8") as f:
        return json.load(f)

LANGUAGE = "en"  # 可以改成 "en" 來切換英文
lang = load_language(LANGUAGE)

def translate(key):
    return lang.get(key, key)

def set_language():
    global LANGUAGE, lang
    print("lang_manager line 16: ", LANGUAGE)
    LANGUAGE = 'en' if LANGUAGE == 'zh' else 'zh'
    print("lang_manager line 18: ", LANGUAGE)
    
    lang = load_language(LANGUAGE)