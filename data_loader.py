import sqlite3
import requests
import json
import time

DB_NAME = "vocabulary.db"

def load_oxford_3000():
    print("正在從 GitHub 獲取 Oxford 3000 單字庫 (CSV)...")
    # 使用 ciwga/Oxford3000_Vocab 的 CSV 資源
    url = "https://raw.githubusercontent.com/ciwga/Oxford3000_Vocab/master/oxford3000_vocabulary_with_collocations_and_definitions_datasets.csv"
    
    try:
        import pandas as pd
        import io
        
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        
        # 使用 pandas 讀取 CSV
        df = pd.read_csv(io.StringIO(response.text))
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        count = 0
        for _, row in df.iterrows():
            word = str(row.get("Word", "")).strip().lower()
            # 取得定義
            definition = str(row.get("Definition", "")).strip()
            # 取得例句
            example = str(row.get("Example Sentence", "")).strip()
            
            if not word or word == "nan":
                continue
                
            try:
                # 這裡使用 INSERT OR REPLACE 因為之前可能已經有 mock 資料
                cursor.execute('''
                INSERT OR REPLACE INTO vocabulary (word, phonetic, definition, example)
                VALUES (?, ?, ?, ?)
                ''', (word, "", definition, example))
                count += 1
            except Exception as e:
                pass
        
        conn.commit()
        conn.close()
        print(f"導入完成！共新增 {count} 個單字。")
        
    except Exception as e:
        print(f"獲取資料時發生錯誤: {e}")
        print("嘗試匯入備用的少量測試資料...")
        import_mock_data()

def import_mock_data():
    mock_data = [
        ("abandon", "/əˈbændən/", "放棄；拋棄", "He had to abandon his plan."),
        ("ability", "/əˈbɪləti/", "能力；才能", "She has the ability to do the job."),
        ("abstract", "/ˈæbstrækt/", "抽象的", "The research is quite abstract."),
        ("academic", "/ˌækəˈdemɪk/", "學術的", "The academic year starts in September."),
        ("accent", "/ˈæksent/", "口音；腔調", "She has a strong French accent.")
    ]
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.executemany('''
    INSERT OR IGNORE INTO vocabulary (word, phonetic, definition, example)
    VALUES (?, ?, ?, ?)
    ''', mock_data)
    conn.commit()
    conn.close()
    print("已匯入 5 個測試單字。")

if __name__ == "__main__":
    load_oxford_3000()
