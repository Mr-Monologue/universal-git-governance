# Embedded C Module · Draft / Preview 0.1.0

[Skill 入口](SKILL.md) 提供新建与维护 C/H 模块的工作流。
它附带 [规范](references/C_CODING_STANDARD.md)、[审查清单](references/REVIEW_CHECKLIST.md)、
[待决项](references/OPEN_DECISIONS.md) 与 [修订背景](references/CHANGE_REVIEW.md)。
Doxygen 强制；其他个人编码风格尚未冻结。没有正式发布 ZIP 或 Release。

## 独立安装

需要时由使用者将完整 `embedded-c-module/` 复制到目标 Agent 支持的技能目录，例如项目的
`.agents/skills/embedded-c-module/`。包含 SKILL.md、README.md、LICENSE、references、assets 和 scripts；
已有同名目录时先比较并处理升级，不直接覆盖。本任务仅在临时目录验证独立副本，不安装到工作项目。
所有文件链接和生成器资源均相对 Skill 目录解析，无需复制 Engineering System 仓库。
支持显式调用的 Agent 可使用 `$embedded-c-module`；其他 Agent 可直接读取 SKILL.md。
先通过一次只读任务确认工具确实加载规则。

## 生成起始文件

Python 3.11+，生成器只用标准库。从 Skill 目录执行，路径有空格时保留引号：

```text
python scripts/new_c_module.py --module adc_scale --output "output folder" --dry-run
python scripts/new_c_module.py --module adc_scale --output "output folder"
```

输出为无业务 API 的配对 C/H 骨架。源文件先包含自己的头文件，再包含标准 `<stddef.h>`，
使尚无业务声明时的翻译单元也可严格编译；实现实际模块后按直接依赖调整。
必须结合需求补充接口、实现及真实 Doxygen 契约，不能把生成结果当作完成的 ADC 驱动。

名称为小写 snake_case（最多 64 个字符），拒绝 C 关键字和 Windows 设备名。
dry-run 仅读取模板、检查冲突并预览路径/内容概要，绝不创建目录或文件。
任一目标存在（包括链接或同名目录）则整体失败；无 `--force`。
通过排他创建保留两个文件，写入异常时关闭句柄并删除本次创建的文件，保留已有文件，
只移除本次创建且仍为空的目录。失败输出明确错误；若回滚也失败，报告残留路径并停止。
这保证可捕获的普通失败回滚，不承诺断电、进程强杀或其他进程同时改写目录时的双文件事务原子性。
退出码：0 成功/预览，2 参数或名称错误，1 文件冲突、读写或回滚失败。

## 规范维护与验证

规范正文唯一人工维护源是工程体系仓库的 `standards/embedded-c/C_CODING_STANDARD.md`。
Checklist、待决项和修订说明分别在同一 standards 目录维护；references 全部为只读分发副本。
在工程体系仓库运行 `python scripts/sync_embedded_c_skill.py` 同步，
运行 `python scripts/sync_embedded_c_skill.py --check` 逐字节检查，CI 只用后者。
同步也复制 [LICENSE](LICENSE)，不添加另一份手工规则源。
独立安装包不需要运行维护同步工具，也不依赖仓库外资源。

轻量验证只检查包结构、frontmatter、链接、模板和副本一致性；不证明业务安全或 Doxygen 全部语义。
修改后执行目标项目批准的编译、测试和 Doxygen，工具缺失报告 NOT RUN。
