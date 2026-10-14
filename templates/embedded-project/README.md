# Embedded Project 模板 · Draft / Preview 0.1.0

本目录是 Profile 与输出模板的唯一人工维护源。

- [firmware](profiles/firmware.json)：纯固件，11 个叶子目录。
- [embedded-fullstack](profiles/embedded-fullstack.json)：固件加硬件/上位机，18 个叶子目录。
- [robotics](profiles/robotics.json)：增加机电、仿真及课程，34 个叶子目录。
- [README 模板](assets/README.md.tpl) 和 [忽略规则模板](assets/gitignore.tpl)：仅生成通用说明与临时文件规则。

Profile 明列所需叶子目录，不使用隐藏继承；父目录由程序推导。数字是领域分类而非阶段，
保留稳定编号和缺号。robotics 的分类不绑定特定项目、厂商或硬件。
JSON schema_version 为 1，仅含 id、description、schema_version、directories。
目录采用安全的相对英文路径，不允许绝对路径、父级跳转、重复、大小写冲突或重叠叶子项。

使用 [embedded-project-init](../../skills/embedded-project-init/README.md) 初始化目录。
维护后在仓库运行 `python scripts/sync_embedded_project_skill.py`；CI 使用 `--check`。
分发副本由脚本生成，禁止在 Skill assets 内手工维护另一套模板。
不得以此模板冻结 C 风格，也不生成业务代码、许可证声明或执行 Git 操作。
