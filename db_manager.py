import sqlite3
import logging
from utils.paths import get_app_root

logger = logging.getLogger(__name__)

class DatabaseManager:
    """管理 SQLite 資料庫的類別，負責 CRUD 操作與版本遷移。"""
    
    CURRENT_VERSION = 1
    DB_NAME = "vocabulary.db"

    def __init__(self):
        self.db_path = get_app_root() / self.DB_NAME
        self.conn = None
        self.init_db()

    def get_connection(self):
        """建立並返回資料庫連接。"""
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """初始化資料庫與表格，並執行版本遷移。"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 1. 建立版本資訊表
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS db_info (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
                ''')
                
                # 2. 建立核心單字表
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS vocabulary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT NOT NULL UNIQUE,
                    phonetic TEXT,
                    definition TEXT NOT NULL,
                    example TEXT,
                    status TEXT DEFAULT 'Learning',
                    mistake_count INTEGER DEFAULT 0,
                    mastery_level INTEGER DEFAULT 0,
                    is_custom BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                
                # 3. 檢查並執行遷移
                self._handle_migration(cursor)
                
                conn.commit()
            logger.info("資料庫初始化與遷移檢查完成。")
        except Exception as e:
            logger.error(f"資料庫初始化失敗: {e}")

    def _handle_migration(self, cursor):
        """處理資料庫版本升級邏輯。"""
        cursor.execute("SELECT value FROM db_info WHERE key = 'version'")
        row = cursor.fetchone()
        
        version = int(row[0]) if row else 0
        
        if version < self.CURRENT_VERSION:
            logger.info(f"偵測到舊版本資料庫 (v{version})，正在升級至 v{self.CURRENT_VERSION}...")
            # 這裡未來可以加入一系列的 if version < X: 升級腳本
            
            # 更新版本號
            cursor.execute("INSERT OR REPLACE INTO db_info (key, value) VALUES ('version', ?)", (str(self.CURRENT_VERSION),))
            logger.info("資料庫升級成功。")

    # --- CRUD 操作 ---

    def get_words(self, query=None, limit=50, offset=0, status=None, mistake_only=False):
        """獲取單字清單，支援搜尋、分頁、錯題篩選。"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                sql = "SELECT * FROM vocabulary WHERE 1=1"
                params = []

                if query:
                    query = query.strip().lower()
                    sql += " AND (LOWER(word) LIKE ? OR definition LIKE ?)"
                    params.extend([f"%{query}%", f"%{query}%"])
                
                if status:
                    sql += " AND status = ?"
                    params.append(status)
                
                if mistake_only:
                    sql += " AND mistake_count > 0"

                sql += " ORDER BY word ASC LIMIT ? OFFSET ?"
                params.extend([limit, offset])

                cursor.execute(sql, params)
                columns = [column[0] for column in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"獲取單字清單失敗: {e}")
            return []

    def get_total_count(self, query=None, status=None, mistake_only=False):
        """獲取單字總數。"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                sql = "SELECT COUNT(*) FROM vocabulary WHERE 1=1"
                params = []

                if query:
                    query = query.strip().lower()
                    sql += " AND (LOWER(word) LIKE ? OR definition LIKE ?)"
                    params.extend([f"%{query}%", f"%{query}%"])
                
                if status:
                    sql += " AND status = ?"
                    params.append(status)

                if mistake_only:
                    sql += " AND mistake_count > 0"

                cursor.execute(sql, params)
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"獲取單字總數失敗: {e}")
            return 0

    def add_word(self, word_data):
        """新增一個單字。"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                INSERT INTO vocabulary (word, phonetic, definition, example, is_custom)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    word_data['word'],
                    word_data.get('phonetic'),
                    word_data['definition'],
                    word_data.get('example'),
                    1 # 手動新增的一律視為自訂
                ))
                conn.commit()
            return True, "新增成功"
        except sqlite3.IntegrityError:
            return False, "單字已存在"
        except Exception as e:
            logger.error(f"新增單字失敗: {e}")
            return False, str(e)

    def update_word(self, word_id, word_data):
        """更新單字資訊。"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                UPDATE vocabulary 
                SET word=?, phonetic=?, definition=?, example=?
                WHERE id=?
                ''', (
                    word_data['word'],
                    word_data.get('phonetic'),
                    word_data['definition'],
                    word_data.get('example'),
                    word_id
                ))
                conn.commit()
            return True, "更新成功"
        except Exception as e:
            logger.error(f"更新單字失敗: {e}")
            return False, str(e)

    def delete_word(self, word_id):
        """刪除單字。"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM vocabulary WHERE id=?", (word_id,))
                conn.commit()
            return True, "刪除成功"
        except Exception as e:
            logger.error(f"刪除單字失敗: {e}")
            return False, str(e)

    def get_random_word(self, status=None):
        """獲取一個隨機單字（用於閃卡或測驗）。"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                sql = "SELECT * FROM vocabulary WHERE 1=1"
                params = []
                if status:
                    sql += " AND status = ?"
                    params.append(status)
                sql += " ORDER BY RANDOM() LIMIT 1"
                cursor.execute(sql, params)
                row = cursor.fetchone()
                if row:
                    columns = [column[0] for column in cursor.description]
                    return dict(zip(columns, row))
                return None
        except Exception as e:
            logger.error(f"獲取隨機單字失敗: {e}")
            return None

    def update_status(self, word_id, status):
        """更新單字的掌握狀態 (Learning/Mastered)。"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE vocabulary SET status=? WHERE id=?", (status, word_id))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"更新單字狀態失敗: {e}")
            return False

    def record_quiz_result(self, word_id, is_correct):
        """記錄測驗結果並更新掌握度等級。"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 獲取目前數值
                cursor.execute("SELECT mastery_level, mistake_count FROM vocabulary WHERE id=?", (word_id,))
                level, mistakes = cursor.fetchone()
                
                if is_correct:
                    level += 1
                    # 連續答對 3 次自動設為 Mastered
                    status = 'Mastered' if level >= 3 else 'Learning'
                    cursor.execute("UPDATE vocabulary SET mastery_level=?, status=? WHERE id=?", (level, status, word_id))
                else:
                    level = 0 # 答錯重置掌握度
                    mistakes += 1
                    cursor.execute("UPDATE vocabulary SET mastery_level=?, mistake_count=?, status='Learning' WHERE id=?", (level, mistakes, word_id))
                
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"記錄測驗結果失敗: {e}")
            return False

    def get_options(self, correct_word_id, count=3):
        """獲取除正確答案外的隨機選項。"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT definition FROM vocabulary WHERE id != ? ORDER BY RANDOM() LIMIT ?", (correct_word_id, count))
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"獲取選項失敗: {e}")
            return []

    # --- 備份與匯出 ---

    def backup_db(self, backup_dir="backups"):
        """備份資料庫檔案。"""
        import shutil
        from datetime import datetime
        try:
            target_dir = get_app_root() / backup_dir
            target_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = target_dir / f"vocabulary_backup_{timestamp}.db"
            
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"資料庫備份成功: {backup_path}")
            return True, str(backup_path)
        except Exception as e:
            logger.error(f"資料庫備份失敗: {e}")
            return False, str(e)

    def export_data(self, format="json", target_path=None):
        """匯出所有單字數據。"""
        import json
        import csv
        try:
            words = self.get_words(limit=999999) # 獲取所有
            
            if format == "json":
                with open(target_path, 'w', encoding='utf-8') as f:
                    json.dump(words, f, indent=4, ensure_ascii=False)
            elif format == "csv":
                if not words: return True, "無數據"
                keys = words[0].keys()
                with open(target_path, 'w', encoding='utf-8-sig', newline='') as f:
                    dict_writer = csv.DictWriter(f, keys)
                    dict_writer.writeheader()
                    dict_writer.writerows(words)
            
            logger.info(f"數據匯出成功 ({format}): {target_path}")
            return True, "匯出成功"
        except Exception as e:
            logger.error(f"數據匯出失敗: {e}")
            return False, str(e)

if __name__ == "__main__":
    # 測試腳本
    logging.basicConfig(level=logging.INFO)
    db = DatabaseManager()
    
    # 驗證版本
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM db_info WHERE key = 'version'")
        print(f"目前資料庫版本: {cursor.fetchone()[0]}")
