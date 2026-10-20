# Engineering System

跨项目、跨 Agent 的工程规范、可执行工作流、模板及工具库。
当前是基础骨架（Scaffold），工作名称不改变远端仓库名称。
目标：规范可复用、任务可执行、产物可验证、版本可追溯。

## 目录导航与资产职责

| 目录 | 职责 | 状态 |
| --- | --- | --- |
| [standards](standards/README.md) | Standard：长期有效的编码、测试和文档规范 | Embedded C Draft v0.1.0 |
| [skills](skills/README.md) | Skill：可执行任务流程与技能索引 | Scaffold；已发布技能见下文 |
| [templates](templates/README.md) | Template：项目及文件生成模板 | Embedded Project Draft |
| [tools](tools/README.md) | Tool：跨项目生成器、安装器和校验工具 | Scaffold |
| [adapters](adapters/README.md) | 不同 Agent 的薄适配入口 | Scaffold |
| [handbook](handbook/README.md) | 沉淀经验证的工程方法与实践 | Scaffold |
| [examples](examples/README.md) | 可复现的通用示例 | Scaffold |
| [tests](tests/README.md) | 通用工具和结构测试 | 基础结构测试已实现 |
| [scripts](scripts/validate_repository.py) | 仓库维护与验证脚本 | 基础验证已实现 |

## 当前模块与版本边界

[git-governance](git-governance/SKILL.md) 是 Stable · 3.0.0 的已发布模块。
[完整 Git 规范](git-governance/references/GIT_GOVERNANCE.md) 是其唯一规则源，
[Cursor 适配](git-governance/adapters/cursor/git-branch-policy.mdc) 引导读取该规则。
正式实现和安装路径保持不变；skills 仅提供索引，不复制或链接第二份实现。
既有 v3.0.0 表示 Git Governance 模块版本，不是 Engineering System 的第三个大版本。
未来聚合发布版本另行决策，各子模块独立记录版本。

[Embedded C Coding Standard](standards/embedded-c/README.md) 已纳入 **Draft v0.1.0**
规范基线、审查清单与验证示例；Doxygen 为强制要求，11 项默认风格已由所有者在 Task 010 批准，项目正式规则优先。
该草案不代表 MISRA C 合规认证，不自动应用到其他项目。
[风格决策评审](standards/embedded-c/STYLE_DECISION_REVIEW.md) 提供技术建议与 C/H 对照，保留历史审议及 11 项 ACCEPTED 状态。
[Skill E2E 验证](handbook/agent-skill-e2e-validation.md) 串联隔离分发、Firmware/Robotics 初始化与 C/H 生成；运行 `python scripts/validate_skill_e2e.py`，真实 Agent 调用单独记录。
[原生 Agent 验收](handbook/native-agent-skill-acceptance.md) 区分发现、调用与产物证据；
[Task 011 收口索引](handbook/skill-native-acceptance-summary.md) 记录 Codex C01—C04 PASS 及原始 C02 日志损坏限制，保留 Task 008 失败历史。
[稳定候选评审](handbook/skill-stable-readiness.md) 与 [发行准备](handbook/release-candidate-notes.md)
仅为评审和提案，不代表 Stable 或 Release 批准。
[embedded-c-module](skills/embedded-c-module/README.md) 为 **Draft / Preview 0.1.0**，
提供独立分发的模块开发工作流与 C/H 骨架生成器；使用已批准默认风格，Skill 仍为 Draft / Preview。
[embedded-project-init](skills/embedded-project-init/README.md) 为 **Draft / Preview 0.1.0**，
提供 firmware、embedded-fullstack、robotics 三种工程目录骨架，支持 Dry Run、冲突保护、幂等生成和只读验证。
完整复制 Skill 后可在仓库外使用 Python 3.11+ 标准库运行；不自动执行 Git 或安装到其他工程。
模板及 Profile 的唯一人工维护源为 [embedded-project](templates/embedded-project/README.md)，分发副本通过同步检查保持一致。
本仓库不收纳其他项目完整源码、公司保密资料、访问密钥或个人敏感资料。

## 安装 Skill

三个 Skill 的统一发现、可重现打包与受控安装见 [分发与兼容性手册](handbook/agent-skills-distribution.md)
及 [Skill Catalog](catalog/skills.json)。`python scripts/skill_dist.py list` 可查看状态；
安装、升级、移除默认仅预览，必须指定目标并显式 `--apply` 才会修改。下述 v3.0.0 旧安装入口保持兼容。

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

## 本地开发、验证与贡献

先阅读 [AGENTS.md](AGENTS.md) 和既有 Git Governance 完整规范。
默认流程为 feature/* → develop → 固定 release → main；独立任务从 develop 派生。
修改、Commit、Push、PR、Merge、Tag、Release 分别核对授权。
使用中文 Conventional Commit，显式暂存任务文件并审查暂存区；完成后停止。

Python 3.11+；旧验证需要 PyYAML 6.0.3，新验证和单元测试只用标准库：

```bash
python -m pip install PyYAML==6.0.3
python scripts/validate.py
python scripts/validate_repository.py
python scripts/validate_embedded_c.py
python scripts/sync_embedded_c_skill.py --check
python scripts/validate_embedded_c_skill.py
python scripts/sync_embedded_project_skill.py --check
python scripts/validate_embedded_project_skill.py
python scripts/validate_skill_distribution.py
python -m unittest discover -s tests -v
git diff --check
```

CI 保留 PR、main/develop/release 和版本 Tag 的触发及旧验证，追加结构、Embedded C 和项目初始化验证与测试。
Embedded C 示例在 CI 用 GCC 的 C11 严格告警编译并运行边界测试，构建输出位于临时目录。
存在 CI 不代表已启用分支保护；验证不替代人工规则审查或 Agent 行为验收。
Git Governance 目录、内容、许可证、v3.0.0 校验和安装入口保持兼容。
问题反馈通过 [Issue](https://github.com/Mr-Monologue/universal-git-governance/issues)，避免私有资料。

## 许可证

采用 [MIT License](LICENSE)。git-governance/LICENSE 保留为发行包许可证副本。
