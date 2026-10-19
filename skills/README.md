# Skills

用途：可执行任务流程与多 Skill 索引。预期内容为任务边界、步骤及验收明确的技能。
边界：规范归 standards，模板归 templates，独立程序归 tools；不复制正式 Skill。
当前状态：技能索引，包含已发布 Git Governance 与两个 Draft Skill。

- [git-governance](../git-governance/SKILL.md)：Stable · 3.0.0；唯一正式实现保持原路径。
- [embedded-c-module](embedded-c-module/SKILL.md)：Draft / Preview · 0.1.0；可独立复制的工作流与安全骨架生成器，个人风格未冻结。
- [embedded-project-init](embedded-project-init/SKILL.md)：Draft / Preview · 0.1.0；三种 Profile 的安全目录初始化与只读验证。完整复制后可独立运行，参见 [安装与 CLI](embedded-project-init/README.md)。不执行 Git，不批准编码风格。
- [embedded-c-standard](../standards/embedded-c/README.md)：Draft v0.1.0 的 Standard；并非已实现的 Agent Skill。

返回 [工程体系入口](../README.md)。

统一分发登记见 [Catalog](../catalog/skills.json)；打包、显式目标安装、完整性校验、升级与安全移除见
[分发与跨 Agent 兼容性手册](../handbook/agent-skills-distribution.md)。两个 Draft Skill 的状态不因分发而改变。
