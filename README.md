# Universal Git Governance

面向开发者及 AI Coding Agents 的通用 Git 分支、提交、协作、验证和发布治理规范。
以可复用的 **Agent Skill** 为核心交付形式，提供 Cursor 适配入口；主要文档使用简体中文，
不依赖具体业务项目、工作区名称或开发语言。

## 适用范围

- 个人、开源、团队和企业软件项目，以及支持 Agent Skills 的开发工具。
- 新项目经明确批准后可采用默认分支模型；既有仓库政策优先，不自动迁移工作流。
- 组织强制安全、审批和身份要求优先。本规范不替代项目测试策略，也不自动授予 Git 操作权限。

## 项目结构

```text
universal-git-governance/
├── README.md
├── LICENSE
├── .gitignore
├── .gitattributes
├── .github/workflows/validate.yml
├── scripts/validate.py
└── git-governance/
    ├── SKILL.md
    ├── references/GIT_GOVERNANCE.md
    └── adapters/cursor/git-branch-policy.mdc
```

[SKILL.md](git-governance/SKILL.md) 是技能入口，
[GIT_GOVERNANCE.md](git-governance/references/GIT_GOVERNANCE.md) 是唯一完整规则源，
[Cursor 适配](git-governance/adapters/cursor/git-branch-policy.mdc) 只负责引导读取完整 Skill。

## 安装 Skill

从 [v3.0.0 发布页](https://github.com/Mr-Monologue/universal-git-governance/releases/tag/v3.0.0)
下载 `git-governance-v3.0.0.zip`。解压后顶层直接是 `git-governance/`，无需再剥离包装目录。
整个目录一起复制，不能只复制 `SKILL.md`。安装包同时保留 MIT 许可证。

以下命令在**目标项目根目录**执行，假设安装 ZIP 已下载到该目录。
若目标技能目录已存在，先比较内容、处理升级，不直接覆盖已有文件。

### PowerShell

```powershell
if (Test-Path .agents/skills/git-governance) { throw '技能已存在，请先比较内容' }
New-Item -ItemType Directory -Force .agents/skills | Out-Null
Expand-Archive -LiteralPath ./git-governance-v3.0.0.zip -DestinationPath .agents/skills
```

### Bash（需已安装 unzip）

```bash
if [ -e .agents/skills/git-governance ]; then
  echo '技能已存在，请先比较内容'
else
  mkdir -p .agents/skills
  unzip -n git-governance-v3.0.0.zip -d .agents/skills
fi
```

也可从本仓库取得完整 `git-governance/` 目录并复制到目标 Agent 的技能目录。
本仓库源码中的根目录 `LICENSE` 也应随复制品保留。
这些安装步骤由使用者在目标项目中主动执行，本仓库不会自动安装到其他项目。

## Codex 使用方式

Codex 支持仓库级 `.agents/skills/git-governance/` 和个人级 `$HOME/.agents/skills/git-governance/`。
本 README 的命令采用仓库级安装，适合团队共享；个人级安装可手动将完整目录放到相应位置。
详见 [OpenAI 官方 Skills 文档](https://developers.openai.com/codex/skills/)。

在 Codex CLI 或 IDE 扩展中可用 `$git-governance` 显式调用，也可通过技能选择器选择。
例如：

```text
请使用 $git-governance 检查当前分支和已有仓库政策，说明下一步开发应从哪里开始。
本次仅做只读检查。
```

工具也可能依据 description 自动选择技能，但安装或调用技能不等于授权提交、推送或发布。
如果未发现新技能，重启工具后检查技能列表及安装路径。

## Cursor 安装方法

先完成上述仓库级 Skill 安装，再从安装后的 Skill 中复制适配文件。
以下 PowerShell 命令同样在目标项目根目录执行：

```powershell
if (!(Test-Path .agents/skills/git-governance/SKILL.md)) { throw '请先安装完整 Skill' }
if (Test-Path .cursor/rules/git-branch-policy.mdc) { throw '规则已存在，请先比较内容' }
New-Item -ItemType Directory -Force .cursor/rules | Out-Null
Copy-Item .agents/skills/git-governance/adapters/cursor/git-branch-policy.mdc .cursor/rules/git-branch-policy.mdc
```

适配文件通过项目根目录路径引用 `.agents/skills/git-governance/` 下的两个 Markdown 文件。
如安装到其他位置，修改这两处引用，并确认 Cursor 能读取。
参见 [Cursor Rules 官方文档](https://cursor.com/docs/rules)。不要把 `.mdc` 当作完整规范。

## 其他 Agent

支持 Agent Skills 的工具：将整个技能目录放入其官方支持的技能位置，检查发现与调用方式。
不支持技能自动发现的工具：在已有项目指令中合并以下引导，按实际安装位置调整路径；不要覆盖现有指令文件。

```text
当任务涉及 Git 分支、暂存、Commit、Push、PR、Merge、Tag 或发布时，
先阅读 .agents/skills/git-governance/SKILL.md 和
.agents/skills/git-governance/references/GIT_GOVERNANCE.md。
遵守已批准的仓库政策及用户当次授权，不自动继续未授权的下一阶段。
```

不保证所有 Agent 自动读取规则；应通过一次只读检查验证其确实加载了完整规范。

## 默认分支模型

```text
feature/* → develop → release → main
```

| 分支 | 职责 |
| --- | --- |
| `main` | 正式发布，默认分支 |
| `develop` | 日常开发集成 |
| 固定 `release` | 内部候选、回归与稳定化；公开仓库中仍对外可见 |
| `feature/*` | 默认从 develop 派生的独立任务 |

新仓库经授权后从同一个初始化提交建立三个长期分支；不创建 `release/v*` 版本分支。
RC Tag 使用 `vX.Y.Z-rc.N`，正式 Annotated Tag 使用 `vX.Y.Z` 并指向 main 的正式提交。
Commit 使用中文 Conventional Commit，保留真实贡献者身份。
`git commit-tree` 仅作为逐次授权的受控例外，不能绕过必需的钩子或审查。
Commit、Push、PR、Merge、Tag、Release 分别核对授权，任务完成后停止。

本项目首次 Bootstrap 经明确授权，直接建立同源 main / develop / release 并发布 v3.0.0；
不制造功能 PR、RC 或多余合并提交。后续独立开发任务按正式规范使用 feature/*。

## 验证与贡献

验证仅依赖 Python 3.11+ 和轻量 YAML 解析器：

```bash
python -m pip install PyYAML==6.0.3
python scripts/validate.py
```

验证覆盖必需文件、Skill 与 Cursor YAML、必需字段、Markdown 围栏、相对文件引用、
安装后的 Cursor 引用及意外的本机绝对路径。它不替代人工规则审查或 Agent 行为验收。
GitHub Actions 对 PR、main / develop / release 更新及版本 Tag 运行同一验证。
仓库分支保护需另行配置；存在 CI 不代表已经启用强制保护。

问题反馈请提交 [Issue](https://github.com/Mr-Monologue/universal-git-governance/issues)，
说明场景、实际行为和期望结果，避免提交密钥或私有资料。
改进前先沟通规则变化，按 feature → develop → release → main 流程提交 PR，
附中文变更说明和验证结果。不要在适配文件中复制完整规范。

## 版本与许可证

首个发布版本：**v3.0.0**。实际发布状态以 GitHub Release 和 CI 记录为准。
项目采用 [MIT License](LICENSE)，版权持有人为仓库所有者 Mr-Monologue。
发行包的 `git-governance/LICENSE` 是根许可证的副本，随技能复制保留。

原始 v3 ZIP 是本次规则来源；工程化只完善安装说明、适配入口、验证和发行元数据。
参考 [Agent Skills 规范](https://agentskills.io/specification)、
[Git commit-tree](https://git-scm.com/docs/git-commit-tree) 和
[Git Tags](https://git-scm.com/book/en/v2/Git-Basics-Tagging)。
