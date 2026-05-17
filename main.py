import sys
import logging
from utils.paths import setup_logging, get_app_root
from db_manager import DatabaseManager
from app import App

def main():
    # 1. 設置全域日誌與異常捕獲
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("正在啟動英文單字學習助手...")

    try:
        # 2. 檢查資料庫狀態
        # 注意: DatabaseManager 的初始化會自動處理 init_db 與 Migration
        db = DatabaseManager()
        
        # 3. 檢查是否有基礎數據 (若為空則提示，或可在此呼叫 data_loader)
        total_words = db.get_total_count()
        if total_words == 0:
            logger.warning("資料庫中無單字數據，請確認是否已執行資料導入。")
        else:
            logger.info(f"成功連線資料庫，目前共有 {total_words} 個單字。")

        # 4. 啟動 GUI 應用程式
        # App 內部會自行重新實例化所需的 Manager，或我們可以修改 App 接受傳入的實例
        app = App()
        app.mainloop()

    except Exception as e:
        logger.critical(f"應用程式啟動失敗: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
