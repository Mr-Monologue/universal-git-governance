---
name: git-governance
description: 通用 Git 协作治理技能。遇到 Git 分支创建、提交、中文提交消息、合并、PR/MR、release 候选验证、Tag、正式发布、hotfix、历史恢复、Agent 操作授权时使用。先检查仓库既有政策，再应用默认 main/develop/release/feature 模型；禁止未授权发布与推送。
metadata:
  version: "3.0.0"
---

# Git Governance — 通用 Agent Skill

本技能可用于不同项目和 Agent。**在执行任何会改变 Git 状态的操作前，先阅读 [`references/GIT_GOVERNANCE.md`](references/GIT_GOVERNANCE.md) 中相应章节。** 该文档是唯一的完整规范来源。

## 触发时机

- 用户需要选择/初始化分支、解释 `main/develop/release/feature` 区别。
- Agent 需要新建分支、暂存、提交、推送、创建 PR/MR、合并、打 Tag 或发布。
- 用户需要中文提交信息、发布说明、冲突处理或紧急修复。
- 遇到已有未提交更改、未知状态、审查门禁或作者署名问题。

## 操作流程

1. **识别优先规则**：阅读仓库现有贡献规范、团队/组织政策以及当前任务权限。本技能的分支模型是默认值，不能据此擅自改造已有仓库。
2. **只读检查**：当前分支、已有修改、分支列表、HEAD、远端信息；保护用户原有更改。
3. **确定当前动作**：开发、集成、RC 验证、正式发布、紧急修复，明确来源和目标。
4. **检查授权**：修改文件、创建分支、Commit、Push、PR、Merge、Tag、Release 等分别判定；任务成功不授予自动执行下一步骤的权限。
5. **执行最小必要动作**：只暂存本任务授权文件；提交前核对暂存清单，测试结论必须真实。
6. **复核并报告**：Commit SHA、测试状态、推送/PR/合并/Tag/Release 的真实状态和下一步阻断。完成后停止。

## 默认分支与发布语义

```text
feature/* → develop → release → main
       开发集成     内部候选     对外正式版
```

- 全新仓库在明确初始化授权下，可从 **`main` 同一初始提交**创建 `develop`、固定 `release`；不额外造提交。
- `feature/*` 默认从 `develop` 派生。修 bug、改文档、实验性变更同样可用 feature。
- `release` 只用于候选验证和稳定化；不从已公开 `main` 常规倒推形成 release。
- `release → main` 需要**本次候选单独、明确的晋升授权**。
- RC Tag `vX.Y.Z-rc.N` 指向候选 `release` 提交；正式 Annotated Tag `vX.Y.Z` 指向最终 `main` 发布提交；Tag 本身**不属于分支**。
- 固定名称 `release`；不创建 `release/vX.Y.Z`。

## 中文 Commit

格式：`type(scope): 中文描述实际变更`。Scope 用真实模块名，不杜撰简称，避免模糊标题。正文说明原因、影响和实际验证结果；组织明确要求其他语言时服从组织政策。

```text
fix(network): 修复断线重连后连接状态未更新的问题
```

不能把仅用于辅助开发的 Cursor 等工具自动当成共同作者；必须保持真实的 Author/Committer/实际贡献者信息。`git commit-tree` 只能是**经过逐次授权的受控例外**，不得用来绕开必需的钩子、签名、安全或审查要求。

## 必须停下的情况

- 用户未批准本次 Commit、Push、Merge、Tag、正式发布或历史改写。
- 出现未知文件更改、合并冲突、未通过的测试或发行内容漂移。
- `release` 包含额外尚未发布功能，而有人要求紧急修复正式版。
- 身份、权限、组织规则和保护要求存在冲突。

## 操作后最小汇报

输出：分支、SHA、修改范围、测试 `PASS / FAIL / NOT RUN`、是否已 Commit / Push / PR / Merge / Tag / Release，以及尚待授权的操作。**不要把“推荐下一任务”视为已获授权。**
