# Feishu Power Skill — MVP 架构

## 定位

一句话：**让 AI agent 像飞书重度用户一样操作飞书，而不只是读写文档。**

飞书官方 MCP 只做了基础文档读写。我们做的是：跨文档工作流 + 多维表格自动化 + 智能内容生成。

---

## 核心能力（MVP 范围）

### 模块1：Bitable 自动化引擎
> 多维表格是飞书的杀手级功能，但 API 操作极其繁琐。

**功能：**
- 自然语言查询多维表格（"找出上周新增的所有待办任务"）
- 批量创建/更新记录（从 CSV/JSON/Markdown 表格导入）
- 跨表关联查询（A 表的客户 → B 表的订单 → C 表的发货状态）
- 字段自动计算（公式生成、数据聚合、统计摘要）
- 定时数据快照（每天自动备份关键表的数据变化）

**为什么先做这个：**
- 我们自己就在用 bitable 管理任务（SkUMdOeXKoyLMUx3NDHcEQG0nqh）
- 零售运营管理大量依赖多维表格
- 飞书官方 MCP 没覆盖 bitable

### 模块2：文档工作流引擎
> 把散落的文档操作串成自动化流程。

**功能：**
- 模板化文档生成（周报/日报/会议纪要，从 bitable 数据自动填充）
- 文档→多维表格双向同步（文档里的 todo 自动同步到 bitable）
- 批量文档操作（搜索替换、格式统一、权限批量设置）
- 知识库自动整理（wiki 节点重组、过期文档归档）

### 模块3：智能报告生成器
> 从数据到洞察，一步到位。

**功能：**
- 从多维表格数据自动生成分析报告（Markdown → 飞书文档）
- 支持图表描述（文字描述数据趋势，因为飞书 API 不支持直接插图表）
- 定时报告（每周一自动生成上周数据摘要）
- 多表汇总（从多个 bitable 汇总数据到一份报告）

---

## MVP 技术架构

```
feishu-power-skill/
├── SKILL.md                    # Skill 入口文档
├── scripts/
│   ├── bitable_engine.py       # 多维表格操作引擎
│   │   ├── query()             # 自然语言 → API 查询
│   │   ├── batch_create()      # 批量创建记录
│   │   ├── batch_update()      # 批量更新记录
│   │   ├── cross_table_join()  # 跨表关联
│   │   └── snapshot()          # 数据快照
│   ├── doc_workflow.py         # 文档工作流引擎
│   │   ├── generate_from_template()  # 模板生成
│   │   ├── sync_todo()         # todo 双向同步
│   │   └── batch_ops()         # 批量操作
│   ├── report_generator.py     # 报告生成器
│   │   ├── analyze()           # 数据分析
│   │   ├── generate_report()   # 生成报告文档
│   │   └── schedule_report()   # 定时报告
│   └── feishu_api.py           # 飞书 API 封装层
│       ├── auth()              # Token 管理
│       ├── bitable.*           # 多维表格 API
│       ├── docx.*              # 文档 API
│       ├── wiki.*              # 知识库 API
│       └── drive.*             # 云盘 API
├── templates/                  # 文档模板
│   ├── weekly_report.md
│   ├── meeting_notes.md
│   └── data_summary.md
└── tests/
    └── test_bitable.py
```

---

## MVP 交付计划

### 今晚（2月19日）
- [x] 架构设计
- [ ] `feishu_api.py` — API 封装层（Token 管理 + 核心 API 封装）
- [ ] `bitable_engine.py` — batch_create / batch_update / snapshot

### 明天（2月20日）你能看到的东西
- 一个能跑的 bitable 批量操作工具
- 演示：从一个 CSV 文件一键导入 50 条记录到多维表格
- 演示：跨两个表做关联查询，输出汇总结果

### 第3-4天
- `doc_workflow.py` — 模板生成 + todo 同步
- `report_generator.py` — 从 bitable 数据生成周报

### 第5-7天
- SKILL.md 完善
- 测试覆盖
- 发布到 ClawHub / GitHub
- 在 Moltbook 发 Build Log

---

## 竞争优势

| 维度 | 飞书官方 MCP | 我们的 Skill |
|------|-------------|-------------|
| 文档读写 | ✅ | ✅ |
| 多维表格自动化 | ❌ | ✅ |
| 跨文档工作流 | ❌ | ✅ |
| 智能报告生成 | ❌ | ✅ |
| 模板系统 | ❌ | ✅ |
| 定时任务集成 | ❌ | ✅（cron） |
| 中文优化 | 部分 | ✅ |

---

## 二阶效应预判

1. **自用价值**：我们自己的任务管理、选品数据、运营报告都能用，不是空中楼阁
2. **内容素材**：开发过程本身就是小红书/Moltbook 的内容（"我给飞书装了个大脑"）
3. **付费潜力**：企业用户对飞书自动化有强需求，这是 SaaS 级别的痛点
4. **生态卡位**：飞书 MCP 生态刚起步，先发者优势明显
5. **风险**：飞书官方可能扩展 MCP 覆盖范围，但我们的跨文档工作流和智能报告是差异化壁垒
