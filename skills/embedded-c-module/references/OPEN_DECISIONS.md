# Embedded C 待决事项 — Draft v0.1.0

[唯一规范正文](C_CODING_STANDARD.md) / [审查清单](REVIEW_CHECKLIST.md) / [完整决策评审](STYLE_DECISION_REVIEW.md)。

所有下列风格均未获用户批准，状态为 OPEN，建议为 PROPOSED。Doxygen 强制原则保持不变，不属于待降级选项。
已有项目正式规则优先；无规则时仅使用明确披露的 Draft 兼容预设，不自动改写项目配置或接口。

| ID | 主题 | 推荐候选 | 状态 | 建议性质 |
| --- | --- | --- | --- | --- |
| C-STYLE-01 | 大括号 | K&R/Attach，函数和控制块同行 | OPEN | PROPOSED |
| C-STYLE-02 | 缩进与 Tab | 4 空格，UseTab Never；TabWidth 显示宽度不等于缩进字符 | OPEN | PROPOSED |
| C-STYLE-03 | 行宽 | 100 列目标；80/120 为项目选项 | OPEN | PROPOSED |
| C-STYLE-04 | 标识符命名 | snake_case + 公开模块前缀；不强制 g_/p_/pf_ | OPEN | PROPOSED |
| C-STYLE-05 | 类型约定 | 公开 module_status；不普遍添加 _t；按语义选整数类型 | OPEN | PROPOSED |
| C-STYLE-06 | C 版本 | 新项目 C11；旧工具链 C99；C23 单独验证 | OPEN | PROPOSED |
| C-STYLE-07 | Doxygen 文本语言 | 项目配置；个人项目默认中文候选 | OPEN | PROPOSED |
| C-STYLE-08 | 质量门禁 | 分层启用并冻结项目工具版本和作用范围 | OPEN | PROPOSED |
| C-STYLE-09 | MISRA/安全层级 | 按风险选定标准、工具、偏离和证据 | OPEN | PROPOSED |
| C-STYLE-10 | 条件比较方向 | 变量在左候选；继承项目规则 | OPEN | PROPOSED |
| C-STYLE-11 | 文件头元数据 | 真实许可证 + Git 历史；不虚构作者/日期 | OPEN | PROPOSED |

Task 003 的候选讨论归并到上述稳定 ID；条件比较和文件头元数据并未遗漏或获批。
完整对比含历史要求、当前行为、替代方案、权衡和影响范围；排版及 API 契约见 [代码对照](examples/style-review/README.md)。
本索引及两份评审材料通过既有同步工具分发，避免独立安装后相对链接断裂；不得手工修改 Skill references。
工程检查通过不等于风格批准。最终选项、适用项目、工具版本及迁移范围须由所有者另行明确决定。
