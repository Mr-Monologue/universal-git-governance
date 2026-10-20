# templates

可复用的工程项目与文件生成模板；不得收纳业务项目源码。

当前状态：Embedded Project Draft / Preview 0.1.0。

[embedded-project](embedded-project/README.md) 是工程目录 Profile 与根文件模板的唯一人工维护源。
提供 firmware（固件）、embedded-fullstack（软硬件及上位机）、robotics（机电控制系统）。
编号稳定且不表示开发阶段；仅生成目录骨架，不生成具体芯片、硬件工程或应用源码。

修改后运行 `python scripts/sync_embedded_project_skill.py`，并用 `--check` 检查分发副本。
用户通过 [embedded-project-init Skill](../skills/embedded-project-init/README.md) 的显式目标 CLI 调用；
支持 Dry Run、无覆盖冲突保护及幂等检查，不影响现有 Git Governance 或 C Module Skill。

返回 [工程体系入口](../README.md)。
