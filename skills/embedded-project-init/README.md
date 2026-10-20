# Embedded Project Init · Draft / Preview 0.1.0

[Skill 入口](SKILL.md) / [Profile 指南](references/PROFILE_GUIDE.md) / [许可证](LICENSE)。
完整复制 `embedded-project-init/` 到 Agent 支持的技能目录即可独立使用；已有目录先比较，不覆盖。
保留 assets、scripts、references 和许可证。无需原仓库、网络或第三方 Python 包；Python 3.11+，CLI 输出 UTF-8。
本任务只在仓库外临时目录测试副本，不安装到其他工作项目。

从 Skill 根目录运行，或用脚本的明确路径；相对 target 始终相对调用者当前目录：

```text
python scripts/init_project.py --target "Example Project" --name "Example Project" --profile firmware --dry-run
python scripts/init_project.py --target "Example Project" --name "Example Project" --profile firmware
python scripts/validate_project.py --target "Example Project" --profile firmware
```

生成器直接使用 target，不额外拼接 name。Profile 仅生成选定目录、根 README、通用 .gitignore、
不含本机路径的 `.engineering-project.json`，以及空叶子目录的 `.gitkeep`。
清单记录初始定义；用户后续新增目录、修改 README 或 .gitignore 可通过只读结构验证，
但再次初始化遇到不同内容会报告冲突，整次不写。初始生成不是持续升级或自动迁移机制。

相同内容标为 UNCHANGED，字节和时间戳不变。dry-run 完全不写入；冲突退出 1，
参数用法错误退出 2，成功/无冲突预览退出 0。没有 force 开关。
目标及其祖先、现有树内的符号链接和 Windows 重解析点保守拒绝，包括无关子目录中的链接。
只在用户控制且无并发修改的目录运行；预检查与排他创建不能提供抵御恶意并发替换的文件系统事务。
普通可捕获失败仅回滚本次创建的文件与空目录；回滚失败报告残留，不声称强杀/断电原子性。
不会删除已有文件、清理用户目录、执行 Git 或安装工具。

模板只在工程体系的 `templates/embedded-project/` 人工维护。
在工程体系运行 `python scripts/sync_embedded_project_skill.py` 同步，`--check` 只读检测缺失、漂移和多余副本。
assets 下 JSON 和模板都是派生副本；独立使用无需同步工具。

本 Skill 不冻结 C 编码风格；不生成许可证/版权声明、特殊硬件工程或业务实现。
