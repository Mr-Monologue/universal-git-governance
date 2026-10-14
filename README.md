# Engineering System

跨项目、跨 Agent 的工程规范、可执行工作流、模板及工具库。
当前是基础骨架（Scaffold），工作名称不改变远端仓库名称。
目标：规范可复用、任务可执行、产物可验证、版本可追溯。

## 目录导航与资产职责

| 目录 | 职责 | 状态 |
| --- | --- | --- |
| [standards](standards/README.md) | Standard：长期有效的编码、测试和文档规范 | Embedded C Draft v0.1.0 |
| [skills](skills/README.md) | Skill：可执行任务流程与技能索引 | Scaffold；已发布技能见下文 |
| [templates](templates/README.md) | Template：项目及文件生成模板 | Scaffold |
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
规范基线、审查清单与验证示例；Doxygen 为强制要求，其余未冻结的风格保留为建议。
该草案不代表 MISRA C 合规认证，不自动应用到其他项目。
embedded-c-module、embedded-project-init 均为 **Planned / 未实现**，尚无新的正式 Skill 或项目模板。
本仓库不收纳其他项目完整源码、公司保密资料、访问密钥或个人敏感资料。

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
python -m unittest discover -s tests -v
git diff --check
```

CI 保留 PR、main/develop/release 和版本 Tag 的触发及旧验证，追加结构、Embedded C 验证与测试。
Embedded C 示例在 CI 用 GCC 的 C11 严格告警编译并运行边界测试，构建输出位于临时目录。
存在 CI 不代表已启用分支保护；验证不替代人工规则审查或 Agent 行为验收。
Git Governance 目录、内容、许可证、v3.0.0 校验和安装入口保持兼容。
问题反馈通过 [Issue](https://github.com/Mr-Monologue/universal-git-governance/issues)，避免私有资料。

## 许可证

采用 [MIT License](LICENSE)。git-governance/LICENSE 保留为发行包许可证副本。
