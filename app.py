import customtkinter as ctk
import logging
from utils.paths import setup_logging
from utils.config_manager import ConfigManager
from utils.asset_loader import AssetLoader
from db_manager import DatabaseManager

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. 初始化基礎設施
        setup_logging()
        self.logger = logging.getLogger(__name__)
        self.config = ConfigManager()
        self.db = DatabaseManager()
        
        # 2. 設定介面主題
        ctk.set_appearance_mode(self.config.get("appearance_mode"))
        ctk.set_default_color_theme(self.config.get("color_theme"))

        # 3. 配置視窗
        self.title("英文單字學習助手")
        self.geometry("1100x700")

        # 設定格線佈局 (1 row, 2 columns)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # 4. 載入導航圖示 (目前為預留，若檔案不存在會返回 None)
        self.home_image = AssetLoader.get_icon("home")
        self.list_image = AssetLoader.get_icon("list")
        self.quiz_image = AssetLoader.get_icon("quiz")
        self.settings_image = AssetLoader.get_icon("settings")

        # 5. 建立側邊導航欄
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(5, weight=1)

        self.navigation_frame_label = ctk.CTkLabel(self.navigation_frame, text=" 學習工具箱",
                                                 compound="left",
                                                 font=ctk.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.home_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, 
                                         text="首頁", image=self.home_image,
                                         fg_color="transparent", text_color=("gray10", "gray90"), 
                                         hover_color=("gray70", "gray30"),
                                         anchor="w", command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.list_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, 
                                         text="單字庫", image=self.list_image,
                                         fg_color="transparent", text_color=("gray10", "gray90"), 
                                         hover_color=("gray70", "gray30"),
                                         anchor="w", command=self.list_button_event)
        self.list_button.grid(row=2, column=0, sticky="ew")

        self.quiz_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, 
                                         text="測驗模式", image=self.quiz_image,
                                         fg_color="transparent", text_color=("gray10", "gray90"), 
                                         hover_color=("gray70", "gray30"),
                                         anchor="w", command=self.quiz_button_event)
        self.quiz_button.grid(row=3, column=0, sticky="ew")

        self.settings_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, 
                                             text="設定", image=self.settings_image,
                                             fg_color="transparent", text_color=("gray10", "gray90"), 
                                             hover_color=("gray70", "gray30"),
                                             anchor="w", command=self.settings_button_event)
        self.settings_button.grid(row=4, column=0, sticky="ew")

        # 6. 頁面視圖實例 (Lazy Loading: 初始為 None)
        self.home_frame = None
        self.list_frame = None
        self.quiz_frame = None
        self.settings_frame = None

        # 7. 預設顯示首頁
        self.select_frame_by_name("home")
        self.logger.info("應用程式主視窗初始化完成")

    def select_frame_by_name(self, name):
        # 1. 更新按鈕背景色
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.list_button.configure(fg_color=("gray75", "gray25") if name == "list" else "transparent")
        self.quiz_button.configure(fg_color=("gray75", "gray25") if name == "quiz" else "transparent")
        self.settings_button.configure(fg_color=("gray75", "gray25") if name == "settings" else "transparent")

        # 2. 延遲加載目標頁面 (Lazy Loading + Dynamic Import)
        if name == "home" and self.home_frame is None:
            from views.home_view import HomeView
            self.home_frame = HomeView(self)
        if name == "list" and self.list_frame is None:
            from views.list_view import ListView
            self.list_frame = ListView(self)
        if name == "quiz" and self.quiz_frame is None:
            from views.quiz_view import QuizView
            self.quiz_frame = QuizView(self)
        if name == "settings" and self.settings_frame is None:
            from views.settings_view import SettingsView
            self.settings_frame = SettingsView(self)

        # 3. 隱藏所有頁面並顯示目標頁面
        for frame in [self.home_frame, self.list_frame, self.quiz_frame, self.settings_frame]:
            if frame:
                if frame == getattr(self, f"{name}_frame"):
                    frame.grid(row=0, column=1, sticky="nsew")
                else:
                    frame.grid_forget()

    def home_button_event(self):
        self.select_frame_by_name("home")

    def list_button_event(self):
        self.select_frame_by_name("list")

    def quiz_button_event(self):
        self.select_frame_by_name("quiz")

    def settings_button_event(self):
        self.select_frame_by_name("settings")

if __name__ == "__main__":
    app = App()
    app.mainloop()
