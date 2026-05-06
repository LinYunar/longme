#!/usr/bin/env python3
"""
Session 文件清理脚本 - LongMe C4
每月1号凌晨3点执行，删除超过60天的旧 session 文件
保留最近30个 session 文件不被清理
损坏文件（<5KB 且 JSON 解析失败）也删除
"""
import os
import json
from pathlib import Path
from datetime import datetime

SESSIONS_DIR = os.path.expanduser("~/.hermes/sessions")
CUTOFF_DAYS = 60
KEEP_RECENT = 30


def cleanup_sessions():
    sessions_dir = Path(SESSIONS_DIR)
    if not sessions_dir.exists():
        print("sessions 目录不存在")
        return
    
    session_files = sorted(
        (p for p in sessions_dir.glob("session_*.json")),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    if not session_files:
        print("没有 session 文件")
        return
    
    now = datetime.now()
    deleted_age = []
    deleted_corrupt = []
    skipped_recent = []
    
    for i, fpath in enumerate(session_files):
        if i < KEEP_RECENT:
            skipped_recent.append(fpath.name)
            continue
        
        mtime = datetime.fromtimestamp(fpath.stat().st_mtime)
        age_days = (now - mtime).days
        
        if age_days > CUTOFF_DAYS:
            try:
                fpath.unlink()
                deleted_age.append(f"{fpath.name} ({age_days}天)")
            except Exception as e:
                print(f"删除失败 {fpath.name}: {e}")
        elif fpath.stat().st_size < 5000:
            try:
                with open(fpath) as f:
                    json.load(f)
            except:
                fpath.unlink()
                deleted_corrupt.append(f"{fpath.name} ({fpath.stat().st_size/1024:.1f}KB)")
    
    print(f"=== Session 清理报告 ({now.strftime('%Y-%m-%d %H:%M')}) ===")
    print(f"扫描文件: {len(session_files)} 个")
    print(f"删除(过期): {len(deleted_age)} 个")
    for d in deleted_age:
        print(f"  - {d}")
    print(f"删除(损坏): {len(deleted_corrupt)} 个")
    for s in deleted_corrupt:
        print(f"  ! {s}")
    print(f"保留(最近30个): {len(skipped_recent)} 个")
    
    remaining = list(sessions_dir.glob("session_*.json"))
    total_size = sum(f.stat().st_size for f in remaining)
    print(f"剩余: {len(remaining)} 个文件, 共 {total_size/1024/1024:.1f} MB")


if __name__ == "__main__":
    cleanup_sessions()
