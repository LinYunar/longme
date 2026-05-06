#!/usr/bin/env python3
"""
Session 摘要写入脚本 - LongMe C3
每10分钟运行一次，将最近会话完整内容写入 SQLite
改动：完整保留最近20条原文，不截断
"""
import sqlite3
import os
import json
import re
from pathlib import Path
from datetime import datetime

DB_PATH = os.path.expanduser("~/.hermes/memories/memory.db")
SESSIONS_DIR = os.path.expanduser("~/.hermes/sessions")

def get_recent_session_content():
    """读取最近 session 文件，提取完整对话内容"""
    sessions_dir = Path(SESSIONS_DIR)
    if not sessions_dir.exists():
        return None, None
    
    session_files = sorted(
        (p for p in sessions_dir.glob("session_*.json")
         if not p.stem.startswith("session_cron_")),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    if not session_files:
        return None, None
    
    latest = session_files[0]
    try:
        with open(latest, 'r') as f:
            data = json.load(f)
        
        messages = data.get('messages', [])
        session_id = data.get('session_id', latest.name)
        created = data.get('session_start', '')[:19]
        if not created:
            fname = latest.stem
            parts = fname.split('_')
            if len(parts) >= 2:
                created = parts[1] + ' ' + parts[2][:6]
        
        recent_msgs = []
        for msg in reversed(messages[-30:]):
            role = msg.get('role', '')
            content = msg.get('content', '')
            if role in ('user', 'assistant') and content:
                recent_msgs.append({'role': role, 'content': content})
        
        return {
            'session_id': session_id,
            'created': created,
            'message_count': len(messages),
            'recent_msgs': recent_msgs[-20:]
        }, latest.stat().st_mtime
    except Exception as e:
        return None, str(e)


def write_summary():
    """写入 session 摘要到 SQLite"""
    conn = sqlite3.connect(DB_PATH)
    data, mtime = get_recent_session_content()
    if not data:
        print(f"无法获取 session 内容: {mtime}")
        conn.close()
        return
    
    current_session_id = data['session_id']
    
    # 去重：同 session_id 只写入一次
    recent = conn.execute("""
        SELECT id, timestamp, summary FROM session_summaries 
        ORDER BY id DESC LIMIT 1
    """).fetchone()
    
    if recent:
        match = re.search(r'会话 (\S+) \(', recent[1] or '')
        last_session_id = match.group(1) if match else None
        if last_session_id == current_session_id:
            print(f"Session {current_session_id} 已写入摘要，跳过")
            conn.close()
            return
    
    # 生成摘要
    summary_parts = []
    summary_parts.append(f"会话 {data['session_id']} ({data['created']})")
    summary_parts.append(f"共 {data['message_count']} 条消息")
    
    if data['recent_msgs']:
        summary_parts.append("=== 最近消息 ===")
        for msg in data['recent_msgs']:
            summary_parts.append(f"[{msg['role']}] {msg['content']}")
    
    summary_text = "\n".join(summary_parts)
    
    # 自动标签提取
    all_text = " ".join([m['content'] for m in data['recent_msgs']])
    keyword_map = {
        '悖论引擎': '悖论引擎', 'BP': 'BP', '融资': '融资',
        '游戏': '游戏', '投资': '投资', '偏好': '偏好',
        '记忆': '记忆', 'session': 'session', 'compaction': 'compaction',
        '压缩': '压缩', 'LongMe': 'LongMe', '万变思集': '万变思集',
        '地火明夷': '地火明夷', '双螺旋': '双螺旋'
    }
    tags = [tag for kw, tag in keyword_map.items() if kw in all_text]
    tags_str = ','.join(tags) if tags else 'auto-summary'
    
    try:
        conn.execute("""
            INSERT INTO session_summaries (channel, summary, key_decisions, key_preferences, projects_status, next_actions, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ('feishu', summary_text, '[]', '[]', '{}', '', tags_str))
        conn.commit()
        print(f"已写入摘要: 会话{data['session_id']}, {data['message_count']}条消息, 标签={tags_str}")
    except Exception as e:
        print(f"写入失败: {e}")
    
    conn.close()


if __name__ == "__main__":
    write_summary()
