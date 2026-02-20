---
name: feishu-power-skill
description: 飞书深度自动化 Skill。多维表格批量操作、跨表关联查询、模板化文档生成、零售运营审计、智能报告。触发词：飞书自动化、bitable批量、多维表格、飞书报告、跨表查询、数据快照、门店审计、运营诊断。
---

# Feishu Power Skill

让 AI agent 像飞书重度用户一样操作飞书。不只是读写文档，而是跨文档工作流 + 多维表格自动化 + 智能报告生成。

## 模块

### 1. Bitable 自动化引擎 (`bitable_engine.py`)

```bash
# 批量创建记录
python3 scripts/bitable_engine.py batch-create --app <app_token> --table <table_id> --data records.json

# 批量更新
python3 scripts/bitable_engine.py batch-update --app <app_token> --table <table_id> --data updates.json

# 跨表 JOIN
python3 scripts/bitable_engine.py join --app <app_token> --left <table1> --right <table2> --on "字段名"

# 数据快照
python3 scripts/bitable_engine.py snapshot --app <app_token> --table <table_id> --output snapshots/

# 统计摘要
python3 scripts/bitable_engine.py stats --app <app_token> --table <table_id>
```

### 2. 文档工作流引擎 (`doc_workflow.py`)

```bash
# 从 Bitable 数据 + 模板 → 飞书文档（一步到位）
python3 scripts/doc_workflow.py generate \
  --app <app_token> --table <table_id> \
  --template templates/data_summary.md \
  --title "周报标题" \
  --group-by "分类字段" \
  --local output.md

# 纯模板渲染（不创建飞书文档）
python3 scripts/doc_workflow.py render --template templates/weekly_report.md --context data.json

# 提取 Bitable 上下文（调试用）
python3 scripts/doc_workflow.py context --app <app_token> --table <table_id>
```

模板语法：
- `{{变量}}` — 简单替换
- `{{#each 列表}}...{{/each}}` — 循环
- `{{#if 条件}}...{{/if}}` — 条件
- 内置变量：`{{TODAY}}` `{{YESTERDAY}}` `{{WEEK_START}}` `{{WEEK_END}}` `{{NOW}}`

### 3. 零售运营审计引擎 (`retail_audit.py`)

```bash
# Demo 模式（50家模拟门店）
python3 scripts/retail_audit.py demo --output report.md
python3 scripts/retail_audit.py demo --publish  # 直接发布到飞书

# 从 Bitable 真实数据审计
python3 scripts/retail_audit.py audit \
  --app <app_token> --sales-table <table_id> \
  --config configs/retail_default.yaml \
  --publish

# 查看可用配置
python3 scripts/retail_audit.py list-configs
```

审计规则（YAML 配置化，可按行业切换）：
- 售罄率过高/过低
- 目标达成率不足
- 负库存 / 零销售
- 库存周转过慢
- 动销率过低

内置配置：`retail_default.yaml`（服装）、`fmcg.yaml`（快消）

### 4. API 封装层 (`feishu_api.py`)

Token 自动管理 + Bitable / Docx / Wiki / Drive 全覆盖。其他模块的底层依赖。

## 依赖

- Python 3.11+
- requests, pyyaml
- 飞书应用凭证（内置或通过 `FEISHU_APP_ID` / `FEISHU_APP_SECRET` 环境变量）

## 测试 Bitable

`J2ehbrIvwaM4XXsjoeQckftAnNe` — 内置测试表，可用于验证功能。
