import PyInstaller.__main__
import os
import sys
from pathlib import Path

def build_app():
    # 取得目前的專案目錄
    project_root = Path(os.getcwd())
    
    # 找出 customtkinter 的安裝路徑 (打包時需要它的 json/tcl 資源)
    import customtkinter
    ctk_path = Path(customtkinter.__file__).parent
    
    # 打包參數配置
    params = [
        'main.py',                      # 入口檔案
        '--name=英文單字學習助手',       # 執行檔名稱
        '--onedir',                     # 打包成目錄模式 (啟動速度提升 10 倍)
        '--windowed',                   # 執行時不顯示控制台視窗
        
        # 包含資產資料夾 (--add-data "來源;目標")
        f'--add-data=assets;assets',
        f'--add-data=vocabulary.db;.',
        
        # 包含 customtkinter 的資源
        f'--add-data={ctk_path};customtkinter',
        
        # 清理快取與暫存
        '--clean',
        '--noconfirm'
    ]
    
    print(f"正在啟動打包程序...")
    print(f"CustomTkinter 路徑: {ctk_path}")
    
    try:
        PyInstaller.__main__.run(params)
        print("\n" + "="*30)
        print("打包完成！請在 'dist/' 資料夾中查看執行檔。")
        print("="*30)
    except Exception as e:
        print(f"打包失敗: {e}")

if __name__ == "__main__":
    # 檢查是否有安裝 pyinstaller
    try:
        import PyInstaller
    except ImportError:
        print("錯誤: 偵測到環境中未安裝 'pyinstaller'。")
        print("請執行以下指令後再試: pip install pyinstaller")
        sys.exit(1)
        
    build_app()
