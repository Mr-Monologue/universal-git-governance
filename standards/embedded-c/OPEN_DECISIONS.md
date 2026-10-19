# Embedded C 待决事项 — Draft v0.1.0

[唯一规范正文](C_CODING_STANDARD.md) / [审查清单](REVIEW_CHECKLIST.md) / [完整决策评审](STYLE_DECISION_REVIEW.md)。

2026-10-20：所有者在 Task 010 对话明确回复“批准全部 11 项”。以下 11 项由 OPEN / PROPOSED 转为 ACCEPTED / DEFAULT。
唯一现行默认值与例外见规范正文第 16 节；本表推荐列保留 Task 006 审议历史，不另立规则源。
Doxygen 强制原则不变；既有项目正式规则优先，不自动改写项目配置或接口。

| ID | 主题 | 历史推荐候选 | 状态 | 当前性质 |
| --- | --- | --- | --- | --- |
| C-STYLE-01 | 大括号 | K&R/Attach，函数和控制块同行 | ACCEPTED | DEFAULT |
| C-STYLE-02 | 缩进与 Tab | 4 空格，UseTab Never；TabWidth 显示宽度不等于缩进字符 | ACCEPTED | DEFAULT |
| C-STYLE-03 | 行宽 | 100 列目标；80/120 为项目选项 | ACCEPTED | DEFAULT |
| C-STYLE-04 | 标识符命名 | snake_case + 公开模块前缀；不强制 g_/p_/pf_ | ACCEPTED | DEFAULT |
| C-STYLE-05 | 类型约定 | 公开 module_status；不普遍添加 _t；按语义选整数类型 | ACCEPTED | DEFAULT |
| C-STYLE-06 | C 版本 | 新项目 C11；旧工具链 C99；C23 单独验证 | ACCEPTED | DEFAULT |
| C-STYLE-07 | Doxygen 文本语言 | 项目配置；个人项目默认中文候选 | ACCEPTED | DEFAULT |
| C-STYLE-08 | 质量门禁 | 分层启用并冻结项目工具版本和作用范围 | ACCEPTED | DEFAULT |
| C-STYLE-09 | MISRA/安全层级 | 按风险选定标准、工具、偏离和证据 | ACCEPTED | DEFAULT |
| C-STYLE-10 | 条件比较方向 | 变量在左候选；继承项目规则 | ACCEPTED | DEFAULT |
| C-STYLE-11 | 文件头元数据 | 真实许可证 + Git 历史；不虚构作者/日期 | ACCEPTED | DEFAULT |

Task 003 的候选讨论在 Task 006 归并到上述稳定 ID；当时 11 项均保持 OPEN。Task 010 经用户批准全部接受，未删除历史分歧。
完整对比含历史要求、当前行为、替代方案、权衡和影响范围；排版及 API 契约见 [代码对照](examples/style-review/README.md)。
本索引及两份评审材料通过既有同步工具分发，避免独立安装后相对链接断裂；不得手工修改 Skill references。
工程检查通过不等于发布批准；项目工具版本、迁移范围及适用安全标准仍由项目决定。
