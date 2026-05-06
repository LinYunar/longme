#!/usr/bin/env python3
"""
立即写入偏好到 memory.db - LongMe C5
对话中确认偏好时调用此脚本，无需等待 cron
用法: python3 ~/.hermes/scripts/preference_writer.py <category> <key> <value>
"""
import sys
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.expanduser("~/.hermes/memories/memory.db")


def write_preference(category, key, value, source="conversation"):
    if not category or not key or not value:
        print("用法: preference_writer.py <category> <key> <value>")
        print("示例: preference_writer.py project 悖论引擎 融资中")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("""
            INSERT INTO preferences (category, key, value, source, confirmed)
            VALUES (?, ?, ?, ?, 1)
        """, (category, key, str(value), source))
        conn.commit()
        print(f"偏好已写入: [{category}] {key} = {value}")
        return True
    except Exception as e:
        print(f"写入失败: {e}")
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) >= 4:
        category, key, value = sys.argv[1], sys.argv[2], sys.argv[3]
    else:
        print("用法: preference_writer.py <category> <key> <value>")
        print("示例: preference_writer.py project 悖论引擎 融资中")
        sys.exit(1)
    
    write_preference(category, key, value)
