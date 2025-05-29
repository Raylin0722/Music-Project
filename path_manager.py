import sys
import os

class PathManager:
    def __init__(self):
        # 判斷是否在打包環境中運行
        if getattr(sys, 'frozen', False):
            # PyInstaller 打包環境
            self.base_path = sys._MEIPASS
        else:
            # 一般開發環境
            self.base_path = os.path.abspath(".")
        
        # 定義各種資源路徑
        self.assets_path = os.path.join(self.base_path, "assets")
        self.lang_path = os.path.join(self.assets_path, "lang")
        self.sounds_path = os.path.join(self.assets_path, "sounds")
        self.pictures_path = os.path.join(self.assets_path, "picture")
        self.screens_path = os.path.join(self.base_path, "screens")
        self.fluidsynth_path = os.path.join(self.base_path, "fluidsynth")
        self.tmp_path = os.path.join(self.base_path, "tmp")
        self.musescore_path = os.path.join(self.base_path, "MuseScorePortable", "MuseScorePortable.exe")
        
        # 輸出診斷信息
        self.print_paths()
        
        # 確保臨時資料夾存在
        self.ensure_temp_folder()
    
    def print_paths(self):
        """輸出所有路徑的診斷信息"""
        print("========== 路徑診斷信息 ==========")
        print(f"程式基礎路徑: {self.base_path}")
        print(f"資源路徑: {self.assets_path}")
        print(f"語言檔案路徑: {self.lang_path}")
        print(f"音效檔案路徑: {self.sounds_path}")
        print(f"圖片路徑: {self.pictures_path}")
        print(f"FluidSynth 路徑: {self.fluidsynth_path}")
        print(f"臨時資料夾: {self.tmp_path}")
        print(f"MuseScore 路徑: {self.musescore_path}")
        print("==================================")
        
        # 檢查關鍵檔案是否存在
        self.check_key_files()
    
    def check_key_files(self):
        """檢查關鍵檔案是否存在"""
        print("\n========== 關鍵檔案檢查 ==========")
        for lang in ["en", "zh"]:
            lang_file = os.path.join(self.lang_path, f"{lang}.json")
            print(f"語言檔案 {lang}.json: {'存在' if os.path.exists(lang_file) else '不存在!'}")
        
        if os.path.exists(self.fluidsynth_path):
            print(f"FluidSynth 目錄: 存在")
            dll_path = os.path.join(self.fluidsynth_path, "libfluidsynth.dll")
            print(f"FluidSynth DLL: {'存在' if os.path.exists(dll_path) else '不存在!'}")
        else:
            print(f"FluidSynth 目錄: 不存在!")
        
        print(f"MuseScore: {'存在' if os.path.exists(self.musescore_path) else '不存在!'}")
        print("==================================")
    
    def ensure_temp_folder(self):
        """確保臨時資料夾存在"""
        if not os.path.exists(self.tmp_path):
            try:
                os.makedirs(self.tmp_path)
                print(f"已創建臨時資料夾: {self.tmp_path}")
            except Exception as e:
                print(f"警告：無法建立臨時資料夾: {self.tmp_path}")
                print(f"錯誤: {e}")
    
    def get_path(self, relative_path):
        """獲取相對於基礎路徑的完整路徑"""
        return os.path.join(self.base_path, relative_path)
    
    def get_asset(self, relative_path):
        """獲取相對於資源資料夾的完整路徑"""
        return os.path.join(self.assets_path, relative_path)

# 創建全域實例
path_manager = PathManager()