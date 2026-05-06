---
name: longme
version: 1.0
description: LongMe（长记忆）— Hermes 记忆系统优化包。由陆离（阿兄）和秋棠共同开发，解决 session 压缩后上下文丢失、摘要质量低、偏好无法立即记忆等问题。
trigger: 记忆调优、LongMe、长记忆、session 压缩、摘要质量、记忆系统优化
author: 陆离 & 秋棠
tags: [memory, hermes, optimization, session, long-term-memory]
created: 2026-05-06
---

# LongMe — 记忆调优包

## 是什么

LongMe 是 Hermes 的记忆系统增强包，由阿兄（陆离）和秋棠共同开发。

解决三个核心问题：
1. **压缩丢失**：compaction 阈值太高，紧急压缩导致上下文被丢弃
2. **摘要太糙**：session_summary_writer 只保留 3 条消息前 100 字，细节全丢
3. **偏好断联**：偏好只能等 cron 写入，对话中断后可能丢失

## 核心文件

| 文件 | 作用 |
|---|---|
| `references/compression_config.yaml` | 压缩参数补丁 |
| `references/session_summary_writer.py` | 升级版摘要写入（完整保留20条） |
| `references/session_cleanup.py` | session 文件清理脚本 |
| `references/preference_writer.py` | 立即写入偏好的 CLI 工具 |

## 改动清单

### C1 + C2：压缩配置（config.yaml）

```yaml
compression:
  enabled: true
  threshold: 0.3        # 原 0.5，30% 就提前压缩
  target_ratio: 0.35     # 原 0.2，保留更多内容
  protect_last_n: 20
```

**效果**：context 占用到 30% 就提前压缩，不会等到 50% 紧急压缩；每次压缩后保留 35% 内容（原来只留 20%）。

### C3：摘要写入升级

**旧版**：只保留 3 条用户消息前 100 字，约 200 字符
**新版**：完整保留最近 20 条消息原文，约 1000+ 字符

**标签自动提取**：基于关键词（悖论引擎/BP/融资/偏好/记忆/session/compaction/压缩）自动打标签，搜索命中率高。

### C4：自动清理

**CronJob**：`0 3 1 * *`（每月1号凌晨3点）
- 删除 60 天前旧 session 文件
- 保留最近 30 个不被清理
- 自动删除损坏的小文件（<5KB 且 JSON 解析失败）

### C5：立即写入偏好

对话中确认偏好时，直接调用：

```bash
python3 ~/.hermes/scripts/preference_writer.py <分类> <键> <值>
```

示例：
```bash
python3 ~/.hermes/scripts/preference_writer.py project 悖论引擎 融资中
python3 ~/.hermes/scripts/preference_writer.py preference 记忆优化 2026-05-06
```

## 安装步骤

### 1. 写入压缩配置

```bash
# 备份原配置
cp ~/.hermes/config.yaml ~/.hermes/config.yaml.bak

# 应用补丁（使用 references/compression_config.yaml）
# 替换 _config_version 和 compression 段
```

### 2. 替换脚本文件

```bash
cp ~/.hermes/scripts/session_summary_writer.py ~/.hermes/scripts/session_summary_writer.py.bak
cp references/session_summary_writer.py ~/.hermes/scripts/session_summary_writer.py

cp references/session_cleanup.py ~/.hermes/scripts/session_cleanup.py

cp references/preference_writer.py ~/.hermes/scripts/preference_writer.py
chmod +x ~/.hermes/scripts/preference_writer.py
chmod +x ~/.hermes/scripts/session_cleanup.py
```

### 3. 创建 CronJob（清理）

```python
# 通过 cronjob tool 创建
# schedule: "0 3 1 * *"
# prompt: "运行 python3 ~/.hermes/scripts/session_cleanup.py"
# deliver: "local"
```

### 4. 重启 Gateway（C1+C2 生效）

```bash
systemctl --user restart hermes-gateway
```

## 测试验证

```bash
# C1+C2 验证
python3 -c "import yaml; c=yaml.safe_load(open('~/.hermes/config.yaml')); print(c['compression'])"

# C3 验证
python3 ~/.hermes/scripts/session_summary_writer.py
# 摘要长度应 > 500 字符

# C4 验证
python3 ~/.hermes/scripts/session_cleanup.py
# 应输出"扫描文件"报告

# C5 验证
python3 ~/.hermes/scripts/preference_writer.py test test_key test_value
# 数据库验证
sqlite3 ~/.hermes/memories/memory.db "SELECT * FROM preferences WHERE key='test_key'"
```

## 注意事项

1. **gateway 重启**后 C1+C2 才生效
2. C5 脚本写入的是 `preferences` 表，不是 `memory_preferences`
3. 清理脚本的 `KEEP_RECENT=30` 和 `CUTOFF_DAYS=60` 可按需调整
4. 损坏文件自动修复（<5KB 且 JSON 解析失败）会在清理时触发

## 维护记录

| 日期 | 动作 | 说明 |
|---|---|---|
| 2026-05-06 | 初始创建 | 阿兄命名"LongMe"，秋棠实现 |
| 2026-05-06 | C1+C2 | threshold 0.5→0.3, target_ratio 0.2→0.35 |
| 2026-05-06 | C3 | 摘要质量 200字符→1000+字符 |
| 2026-05-06 | C4 | 每月清理 CronJob 创建 |
| 2026-05-06 | C5 | 立即写入偏好脚本创建 |
