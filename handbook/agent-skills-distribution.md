# Agent Skill 分发与兼容性基础

本工具仅管理本仓库现有三个 Skill。统一目录是 [catalog/skills.json](../catalog/skills.json)，
不复制 SKILL.md 正文，不迁移旧目录，也不把聚合仓库版本用作模块版本。

| Skill | 状态 | 唯一源码目录 |
| --- | --- | --- |
| git-governance | Stable 3.0.0 | `git-governance/` |
| embedded-c-module | Draft / Preview 0.1.0 | `skills/embedded-c-module/` |
| embedded-project-init | Draft / Preview 0.1.0 | `skills/embedded-project-init/` |

Git Governance v3.0.0 原发行包、许可证、内容和旧安装入口保持原样。
这里生成的是同一源码的新增可重现打包方式，不替换历史发行 ZIP，也不保证与旧 ZIP 字节相同。
两个 Draft Skill 不因可安装而成为 Stable。C 规范待决风格继续 OPEN，Doxygen 强制原则不变。

## 使用前提与命令

分发管理工具使用 Python 3.11+ 和仓库现有 PyYAML 6.0.3；没有网络下载、Git 操作或全局设置修改。
已安装 Skill 的两个生成器仅需 Python 3.11+ 标准库，无需分发工具、PyYAML 或原仓库。
所有命令从 Engineering System 根目录执行，目标是明确指定的隔离目录。
下面 PowerShell 用临时路径演示；在真实项目操作须由使用者另行授权。

```powershell
$testRoot = Join-Path $env:TEMP 'engineering-skill-distribution-demo'
$installRoot = Join-Path $testRoot 'project/.agents/skills'
$packageRoot = Join-Path $testRoot 'packages'
python scripts/skill_dist.py list
python scripts/skill_dist.py pack --skill git-governance --output-dir "$packageRoot"
python scripts/skill_dist.py pack --skill embedded-c-module --output-dir "$packageRoot"
python scripts/skill_dist.py pack --skill embedded-project-init --output-dir "$packageRoot"
python scripts/skill_dist.py install --skill embedded-project-init --target-dir "$installRoot"
python scripts/skill_dist.py install --skill embedded-project-init --target-dir "$installRoot" --apply
python scripts/skill_dist.py verify --skill embedded-project-init --target-dir "$installRoot"
python scripts/skill_dist.py upgrade --skill embedded-project-init --target-dir "$installRoot"
python scripts/skill_dist.py upgrade --skill embedded-project-init --target-dir "$installRoot" --apply
python scripts/skill_dist.py remove --skill embedded-project-init --target-dir "$installRoot"
python scripts/skill_dist.py remove --skill embedded-project-init --target-dir "$installRoot" --apply
```

安装、升级、移除不带 `--apply` 均零写入，不创建管理目录或导入缓存。
`verify` 和 `list` 只读。`pack` 的显式 `--output-dir` 授权生成 ZIP 与 SHA-256 旁文件。
命令成功返回 0，冲突/验证失败返回非零；参数缺失由 argparse 返回 2。
相同的受管安装返回 UNCHANGED；内容不同须使用 upgrade，没有 force 或自动接管。
升级按当前已验证源内容进行，不要求版本字符串变化；测试用隔离源码夹具模拟内容升级，未修改真实 Skill。

打包使用固定时间戳、权限、排序和 ZIP_STORED，稳定字节不依赖压缩库版本。
文件名为 `<name>-<version>-<channel>.zip`，顶层直接是 `<name>/`。
SHA-256 输出在终端和同名 `.zip.sha256` 文件中；相同产物不重复写入，不同内容同名产物拒绝覆盖。
排除 Git、虚拟环境、缓存与临时文件，同时验证最终包内相对链接。
源与规范/模板分发副本漂移时失败，不自行同步，应在单独授权任务中解决。
本版安装/升级读取已验证的正式源码目录；不接受外部 ZIP 安装输入，也不执行解压后的脚本。
ZIP 路径和条目类型仍独立校验，并有恶意路径测试。手动解压的目录不自动成为本工具的受管安装。

## 管理记录与安全边界

安装目录示例：

```text
.agents/skills/
├── embedded-project-init/       # 逐文件与源内容一致
├── other-user-skill/            # 不接管
└── .skill-dist/
    └── embedded-project-init.json
```

每个管理记录包含 schema、模块名、版本、channel、目录清单和文件 SHA-256，不保存用户名或本机绝对路径。
记录位于 Skill 外，不进入源码或发行 ZIP。校验独立于当前源码内容；旧安装不会因源码升级而被误判为用户修改。
未知文件（包括空目录、运行时缓存）、丢失文件、修改内容或缺失记录均阻止自动升级/移除。
运行已安装 Python 工具时可用 `python -B` 避免缓存。检测到缓存也不擅自删除，应由用户确认处理。
SHA-256 用于发现漂移，不是签名或来源认证；能同时篡改安装和管理记录的攻击者不在可信边界内。

显式目标不能位于源仓库内或其祖先目录。所有相关路径组件拒绝符号链接、Junction/重解析点、
硬链接文件、路径穿越、设备名、同名非目录和不安全 ZIP 路径。
已有非管理 Skill 不接管；管理记录损坏、锁或残留事务目录存在时停止并报告，不能自动清理。
工具不遍历或删除其他 Skill 内容。

应用时用独占锁协调本工具的操作。在管理目录内准备完整新副本，核验后把旧 Skill 与记录保留到事务目录，
再提升新副本和记录。普通失败尝试恢复旧目录/记录；仅删除本次新增内容。
移除也先保留旧副本，再提交记录变更，最后校验精确清单并逐文件删除、逐空目录移除。
不使用递归删除接管未知文件。提交后的清理失败会报错并保留恢复位置，而不假称完整成功。
不保证断电、强杀或其他进程恶意并发替换路径时的原子性；锁仅协调本工具。
出现恢复残留时，人工核对报出的路径、旧记录和副本，先备份，再决定恢复，禁止盲目删锁重试。

## 文件格式与 Agent 发现位置

开放 Agent Skills 格式由 `SKILL.md`（包含 name、description 的 YAML frontmatter）和可选 scripts、references、assets 组成。
格式可移植不等于每种 Agent 都会发现或成功执行。参考 [Agent Skills 规范](https://agentskills.io/specification)。

以下路径于 2026-10-15 核对当前官方文档；本轮没有实际启动三个 Agent 对新安装执行发现/调用验收。

| Agent | 项目级位置 | 个人级位置示例 | 官方依据 |
| --- | --- | --- | --- |
| Codex | `.agents/skills/`；从当前目录向仓库根搜索 | `~/.agents/skills/` | [OpenAI Build skills](https://learn.chatgpt.com/docs/build-skills) |
| Cursor | `.agents/skills/`、`.cursor/skills/` | `~/.agents/skills/`、`~/.cursor/skills/` | [Cursor Agent Skills](https://cursor.com/docs/skills) |
| GitHub Copilot | `.agents/skills/`、`.github/skills/`、`.claude/skills/` | `~/.agents/skills/`、`~/.copilot/skills/` | [GitHub 添加 Agent Skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills) |

项目级优先选 `.agents/skills/`，无需为三个 Agent 维护三份源码。个人级影响多个项目，须单独决定，工具不默认选择。
本地安装不意味着云端 Agent 或远端机器自动同步；应分别提供文件和运行环境。
例如 Cursor 官方仅在用户启用相应功能后同步特定个人目录，不能推断本机 `.agents/skills/` 已传到远端。

手动调用：Codex 可在技能选择入口明确选用；Cursor 可在 Agent 的 `/` 入口选择；
Copilot 可明确要求使用指定 Skill，并检查其实际读取的文件和资源。
自动发现还取决于描述匹配、Agent 版本、产品入口和配置，不保证每次自动触发。
安装及技能调用均不授予 Commit、Push、Merge 或发布权限，继续遵守目标项目规则和当次用户授权。
原 Git Governance 的 Cursor 适配文件随包保留；本工具不将其自动写入目标 `.cursor/rules/`。

## 验证与证据分层

```powershell
python scripts/validate_skill_distribution.py
python -m unittest discover -s tests -v
```

| 证据层 | 本任务验收方式 | 状态 |
| --- | --- | --- |
| 文件格式 | Catalog、源路径、许可证、frontmatter、包内相对链接与副本一致性 | 自动化验证 |
| 独立运行 | 隔离安装后使源夹具不可用，生成 C/H 和工程骨架、运行结构验证 | 自动化验证 |
| Codex 真实发现/调用 | 在另行授权的 Agent 会话确认技能已加载及操作结果 | NOT RUN |
| Cursor 真实发现/调用 | 同上，不以文档推断 | NOT RUN |
| GitHub Copilot 真实发现/调用 | 同上，不以文档推断 | NOT RUN |
| GitHub Actions | 本地运行对应检查并解析 YAML，未 Push 不触发远端 | NOT RUN |

Windows 符号链接测试缺少权限时报告 NOT RUN，并另行测试真实 Junction；Linux CI 可执行符号链接测试，跳过 Windows 专有 Junction 场景。
故障注入覆盖部分写入失败、安装锁写入失败、升级提升失败恢复、移除记录失败恢复。
所有测试使用隔离临时目录，不安装到真实业务工程或全局 Agent 目录。

返回 [工程体系入口](../README.md)。
