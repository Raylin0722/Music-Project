import json
import pygame
import os
from path_manager import PathManager  # 導入類，不是實例

# 獲取 PathManager 實例
path_manager = PathManager()

def load_language(lang_code):
    try:
        # 使用 path_manager 獲取正確的文件路徑
        file_path = os.path.join(path_manager.lang_path, f"{lang_code}.json")
        print(f"嘗試載入語言檔案: {file_path}")
        
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"載入語言檔案錯誤: {e}")
        # 嘗試使用相對路徑作為後備方案
        try:
            backup_path = f"assets/lang/{lang_code}.json"
            print(f"嘗試使用備選路徑: {backup_path}")
            with open(backup_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as backup_e:
            print(f"備選路徑也失敗: {backup_e}")
            return {}

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