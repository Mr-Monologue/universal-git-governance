# Agent 工程入口

先检查仓库已有规范、工作区状态与用户当次授权。
Git 操作先阅读并遵守 [Skill](git-governance/SKILL.md) 和
[完整参考规范](git-governance/references/GIT_GOVERNANCE.md)，不在此重复规则。

- 新资产按 Standard / Skill / Template / Tool 职责进入对应目录；Handbook 只记录经验证的实践。
- 不凭空宣称 Planned 组件已实现；保留 git-governance 唯一正式实现及安装路径。
- 提交说明使用中文，类型与 scope 可用英文；保留真实作者身份。
- 显式暂存授权范围文件，提交前审查暂存文件清单和差异，避免 git add -A 等无边界暂存。
- 本地编辑、Commit、Push、PR、Merge、Tag、Release 分别受权；任务结束不自动进入下一阶段。
- 不处理、发布或提交公司保密数据、访问密钥或私人资料。
- 规则冲突时以组织/用户明确授权和仓库强制策略优先，列出冲突并停止高风险动作。

本地验证命令与目录职责见 [README](README.md)。
