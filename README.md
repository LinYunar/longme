# LongMe — Hermes 长记忆系统优化包

> 解决 session 压缩后上下文丢失问题，由陆离和秋棠共同开发。

## 目录结构

```
longme/
├── SKILL.md                          # 完整技能文档
└── references/
    ├── compression_config.yaml       # C1+C2 压缩参数补丁
    ├── session_summary_writer.py     # C3 摘要写入升级
    ├── session_cleanup.py            # C4 清理脚本
    └── preference_writer.py          # C5 立即写入偏好
```

## 功能模块

| 模块 | 功能 |
|------|------|
| C1 压缩参数调优 | 优化 Hermes session 压缩算法参数 |
| C2 摘要质量升级 | 提升压缩后摘要的信息保留度 |
| C3 摘要写入升级 | 加快摘要写入速度，减少 IO 阻塞 |
| C4 清理脚本 | 自动清理过期 session 文件 |
| C5 立即写入偏好 | 偏好修改即时持久化，无延迟 |

## 触发词

`LongMe`、`长记忆`、`记忆调优`、`session压缩`、`摘要质量`

## 使用方法

```bash
# 在 Hermes 中加载技能
skill_load("longme")

# 或触发关键词
"LongMe"
```

## 背景

Hermes 的 session 压缩机制在长对话场景下会丢失关键上下文，影响 AI 对项目背景、用户偏好的理解。LongMe 通过五层优化实现几乎无损的上下文保持。

---

MIT License
