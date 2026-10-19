---
name: embedded-c-module
description: 创建或维护嵌入式 C/H 模块、公开接口文档和驱动/实时模块时，按项目规范设计 API、编写 Doxygen 契约并验证实现。用于模块开发，不用于全工程重写或 MISRA 合规认证。
metadata:
  version: "0.1.0"
  status: "draft"
---

# Embedded C Module — Draft / Preview

生成器只创建起始文件，业务接口和实现由任务需求决定。Doxygen 是强制要求，默认风格按规范正文第 16 节的所有者批准值执行；不能当作其他组织已批准的政策。

## 工作流

1. 识别目标项目已有规范、C 标准、工具链、平台、RTOS、文件布局及本次授权。既有正式规则优先；维护旧文件先检查 ABI、调用方及测试。
2. 理解模块需求和公开 API。实现前按需阅读 [完整规范](references/C_CODING_STANDARD.md) 的相关章节；涉及指针/单位读 4–6 节，并发/实时读 9 节，Doxygen 读 10 节。遇到风格冲突读 [决策历史](references/OPEN_DECISIONS.md)，需要原规则背景再读 [修订说明](references/CHANGE_REVIEW.md)。
3. 新文件可使用 [生成器](scripts/new_c_module.py) 与 [头文件](assets/module.h.tpl)、[源文件](assets/module.c.tpl) 模板。先 dry-run 检查目的路径，再在授权目录生成。既有文件直接做必要的局部维护，不运行生成器覆盖，不做无关重排、全量格式化或 ABI 改动。
4. 创建或修改 C/H 时，先起草并随实现更新真实 Doxygen 契约。文件顶部必须有 `@file`、`@brief`；公开函数、类型和有意义的公共宏/常量必须文档化。相关时说明参数输入/输出方向、单位、范围、错误码、所有权与生命周期、ISR/RTOS/DMA、线程安全、重入性及执行时间约束；按实际语义添加 `@param`、`@retval`、`@note`、`@warning` 等，不机械填空。公式先定义符号、单位和物理意义，再给公式及适用条件。
5. 完成业务实现后用 [Checklist](references/REVIEW_CHECKLIST.md) 审查本次变更。运行实际可用的编译告警、边界测试、格式和 Doxygen 检查；构建输出放临时目录，不安装工具来掩盖缺项。
6. 报告修改范围、采用的项目规则/默认值、实际命令及 PASS / FAIL / NOT RUN、未解决风险。生成成功不等于业务模块完成，不宣称 MISRA 合规或硬实时保证。

## 已批准默认风格与操作边界

目标项目无正式规则时，采用 [规范正文第 16 节](references/C_CODING_STANDARD.md#16-已批准的默认风格与项目覆盖) 的已批准默认值及例外。规则正文是唯一人工维护源；Skill 保持 Draft / Preview 0.1.0，风格批准不等于稳定版发布。目标项目有其他命名需求时直接按其规则创建文件，本生成器只接受可移植的 snake_case 文件名。

调用本 Skill 不授予覆盖、全量格式化、软件安装、Git Commit/Push 或跨项目修改权限。Git 操作遵循目标项目已有治理和本次授权；不要求安装另一 Skill 才能使用本 Skill。
不得把 AI、Cursor、Codex 写为作者或共同作者，不编造版权人、日期或许可证。引用的 references 是脚本生成的分发副本，不在安装目录手工修订规范。

用法与失败回滚边界见 [README](README.md)。
