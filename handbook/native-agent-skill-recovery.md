# Codex 原生验收恢复与权限定位

Task 009 当前为 **PARTIAL / USER ACTION REQUIRED**。文档、安装复核与脚本回归完成，
普通用户终端对照和新的原生调用尚未执行。[Task 008](native-agent-skill-acceptance.md) 的
PARTIAL/BLOCKED 是历史事实，不因本次版本查询成功而改成 PASS。

## D0：已确认的事实

- Task 008 在 Agent 工具环境中启动原生 exec，退出码 1，stdout 为 0 字节。
  stderr 包含 arg0 缓存清理/PATH alias 创建的访问警告，随后 `os error 5`。
- Task 009 当前工具环境为 PowerShell 7.6.5，工作目录为本仓库。
  `Get-Command codex -All` 与 `where.exe codex` 指向同一个 Application。
- 本轮只尝试一次 `codex --version`：输出 `codex-cli 0.162.0-alpha.17.2`，退出码 0，
  仍伴随 arg0 缓存访问警告。没有反复启动第二个 Codex。
- 因警告仍在，本轮不再调用 `exec --help`；Task 008 的帮助记录仅供历史参考。
- 失败发生在可观察的 Agent 回答/调用事件之前；**具体失败的内部操作尚未定位**。
  缓存警告与最终错误是否同一根因也未证实，不能断言 Skill 加载阶段已经开始或完全未开始。

版本查询成功只证明可执行文件能启动并完成这条轻量命令，不证明完整会话、认证、网络或 Skill 加载正常。
尚无证据把错误归因于 Skill 内容、CLI 缺陷、系统权限或安全软件。

## D1：普通终端对照决定后续分支

| 实际观察 | 可以得出的结论 | 下一步 |
| --- | --- | --- |
| Agent 内 exec 被拒，普通终端会话正常 | 执行上下文不同；继承权限边界是可能解释 | 仅在用户主动启动的隔离原生会话继续验收 |
| 普通终端版本查询或会话也失败 | 主机执行/会话层仍阻断，不能归因 Skill | 保存退出码及错误，停止；不提权或修改安全策略 |
| 原生会话能启动，但未发现项目 Skill | 可以开始检查发现层 | 核对实际工作根、项目级安装、原生技能列表和元数据 |
| 发现但没有读取或执行工作流 | 只有 DISCOVERED 证据 | INVOKED、OUTPUT_VERIFIED 保持 NOT RUN |

以上均为条件分支，不是本轮已观察的主机结果。当前普通终端结果为 **NOT RUN**。

## 已准备的隔离现场

优先复用 Task 008 的 `<isolation>`：

```text
<isolation>/
├── skill project/.agents/skills/   # 三个受管 Skill
├── governance project/            # 独立 Git，政策 trunk + topic/*
│   └── .agents/skills/git-governance/
├── sentinel.txt
├── evidence/                      # Task 008 原始记录，不改写
└── Task009_Validation/             # 本轮登记、哈希、用户记录模板
```

Catalog schema_version=1；git-governance Stable 3.0.0，两个 Embedded Skill 为 Draft/Preview 0.1.0。
本轮四个安装均经官方仓库管理 CLI verify，通过完整性检查并与当前分发源码逐字节比较。
文件 SHA-256 清单、哨兵 SHA-256/大小/mtime_ns、治理仓库文件清单已固定在仓库外记录中。
`skill project/firmware output` 尚不存在，是后续 C02/C03 唯一允许创建产物的目录。
这些是准备证据，不计 DISCOVERED 或 INVOKED。

实际绝对路径在本次仓库外 `Task009_Validation/USER_STEPS.txt` 与最终报告中提供。
临时目录如被系统清理，停止使用旧路径，重新准备并登记；不要改为真实业务工程。

## 用户操作：普通、非管理员 PowerShell

这些命令须由用户主动执行。本 Agent 不代替用户启动外部普通终端，不要求安装/升级或修改审批、沙箱、ACL、执行策略。

```powershell
Get-Command codex -All
where.exe codex
codex --version
$LASTEXITCODE
```

记录输出和警告。版本查询失败时停止，并保存最小复现。成功后使用本次准确路径：

```powershell
Set-Location -LiteralPath '<isolation>\skill project'
codex
```

不要使用 bypass 参数。若会话启动失败，记录错误及退出码后停止，不循环重试。
如果当前 CLI 入口不同，先看普通终端的实际 `codex --help`，不能推定旧参数一直适用。
不要粘贴凭据、环境变量全集或用户配置内容。

以下文本粘贴进 **Codex 对话**，不是 PowerShell；`$skill-name` 是明确调用文本，不能让 shell 当变量展开。

### C01：窗口 A，skill project

```text
请列出当前新会话原生可发现的项目级 Agent Skills，注明 git-governance、embedded-project-init、embedded-c-module 是否被识别及其 SKILL.md 路径。不要修改文件，不要通过列目录后推断原生发现；不能观察到原生发现时明确说证据不足。
```

保留可见技能列表、实际选择/读取动作及回复。没有原生证据则停止依赖场景，不能用 verify 成功顶替。

### C04：窗口 B，独立治理测试仓库

在另一个普通 PowerShell 中进入 `<isolation>\governance project` 并启动 `codex`。
它只安装了 git-governance，不要求在此发现两个 Embedded Skill。

```text
请使用 $git-governance，只读检查当前隔离 Git 仓库的政策、分支、状态和权限边界，并建议下一开发分支。先读取现有 AGENTS.md 和 Skill 完整规范。仅可读取，不初始化 Git、不创建/切换分支、不 add/commit/push/merge/tag，不修改配置或任何文件。说明现有 trunk/topic 政策与默认三长期分支模型的区别，不实施建议。
```

核对实际工具动作及 Git 元数据差异，不只看最终文字。准备阶段已有 `git init` 不属于 C04 Agent 行为。

### C02：回到窗口 A

```text
请使用 $embedded-project-init，在当前隔离工作区内的 firmware output 子目录创建名为 Native Recovery Firmware 的 firmware Profile。先读取 Skill、检查目标，再 dry-run、生成并执行只读结构验证。只允许写该子目录，不覆盖已有文件，不修改 .agents/skills、全局配置或其他目录，不安装软件，不执行任何 Git 写操作。报告实际路径和命令。
```

### C03：仍在窗口 A

```text
请使用 $embedded-c-module，在 firmware output/05_Firmware/Core 创建 adc_filter.h/.c 教学模块：对有效范围 0..4095 的 ADC 样本作两点整数平均，明确取整规则；非法输入或 NULL 输出指针返回错误且保持输出不变。先读取目标项目规则与 Skill，检查同名文件并预览，不覆盖已有文件。编写 Doxygen 文件头、公开类型/API 契约，说明输入/输出方向、code 单位、边界、返回值、对象有效期、调用上下文及 ISR 限制。11 项风格仍 OPEN，不改规范或 Skill。只允许写 firmware output 内的代码、测试和构建记录；使用已有工具编译、测试、Doxygen 及适用格式检查，缺工具记 NOT RUN，不安装软件，不执行 Git 写操作。
```

普通终端能启动不代表 C01–C03 一定通过。按实际结果逐项登记，禁止由验收者代做产物后冒充 Agent 生成。

## 记录与复核

在仓库外 `USER_RESULTS.md` 填写原始提示词、实际回复摘要、工具读取/执行证据、产物路径、命令与退出码。
每项独立记录 DISCOVERED、INVOKED、OUTPUT_VERIFIED；不可见内部事件就写不可见，不自行补写。
只识别名字不等于使用 Skill，仅生成文件不等于产物检查通过。

C05 应在人工场景后再次核对哨兵、四项安装 verify、治理仓库文件哈希与 Git 状态，确认新增产物只在 firmware output。
运行缓存与用户全局配置应分别描述；没有前后证据时不能声称全盘无变更。
本轮 C05 仅准备范围检查 PASS，**人工调用后的 C05 仍 NOT RUN**。
出现越界、未授权 Git 写入或冒称调用立即判 FAIL 并停止，保留证据。

| 项目 | 本轮状态 |
| --- | --- |
| D0 环境事实、安装/哈希复核、文档/脚本回归 | PASS（限定上述范围） |
| D1 普通非管理员终端对照 | USER ACTION REQUIRED / NOT RUN |
| C01 | Task 008 BLOCKED；本轮用户复验 NOT RUN |
| C02–C04 | NOT RUN |
| C05 人工调用后复核 | NOT RUN；准备范围复核 PASS |
| 原生产物编译、Doxygen、clang-format | NOT RUN，尚无本轮原生产物 |
| Cursor/Copilot | NOT RUN，不属于本轮操作范围 |

本轮继续保留 [原生验收指南](native-agent-skill-acceptance.md) 的证据标准和脱敏规则。
现有自动化 PASS 与原生验收状态分别报告。无需增加安装框架或修改 Skill，收到真实人工记录后才更新相应状态。
完成准备和文档提交后停止等待用户结果，不自动启动下一任务。

## Task 010 前置复核：用户提供的 C01 成功摘录

证据索引：[用户终端日志摘录](task009-c01-user-supplied-evidence.md)。
附件 SHA-256：`60da2e14f17810543dde12331e01c567e6c2e382bc90adab1d00f96fee85f9d7`。
成功 Session ID：`01a154cd-b23a-7961-9658-245eba557ed1`，工作目录 `G:\Skill-Acceptance-009`。
本次实际读取的是用户提供的 Markdown 终端日志摘录，未取得原生 `.jsonl` 会话文件。
Task 010 第 2.3 节允许用户日志证据，没有强制原始会话文件要求。

- 原生发现 PASS：依据同一会话可用 Skills 清单的用户摘录，区别于本地列目录。
- 正文读取 PASS：三个 `READ_STATUS: OK`；记录说明 Get-Content 实际读取并输出 Unicode 转义正文，退出码 0。
- 字段与约束提取 PASS：Git Governance 3.0.0；两个 Embedded Skill 0.1.0 / draft。
  Governance 独立授权、完整规范与钩子边界；C Module Doxygen、dry-run、防覆盖与 ABI 边界；
  Project Init 目标授权、dry-run、重解析点拒绝及只读验证均见摘录第 4 节。
- C01 PASS 限定于上述用户提供证据；C02–C04 和人工调用后的 C05 仍 NOT RUN，整体仍 PARTIAL。

临时目录访问失败与 G 盘成功来自不同执行上下文；只能说明结果存在对照，
不足以把失败确定归因于单一权限、CLI 或 Skill 加载因素。不覆盖历史失败记录。
以上是对本文早期 NOT RUN 状态的后续更新；不是声明已经独立复验原生会话。
