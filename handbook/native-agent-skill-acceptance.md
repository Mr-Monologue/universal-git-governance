# Codex 原生 Skill 调用验收

本指南区分真实 Agent 会话与 [脚本 E2E](agent-skill-e2e-validation.md)。
执行脚本成功、读取 SKILL.md 或 Agent 自称使用了 Skill，均不能单独证明原生发现与调用。
本轮 Task 008 为 **PARTIAL / BLOCKED**：准备和回归完成，原生会话启动被本机访问权限阻断。

后续跟踪见 [Task 009 恢复与权限定位](native-agent-skill-recovery.md)。该跟踪不改写 Task 008 的阻断事实；普通用户终端原生复验仍待实际执行。

## 环境与隔离准备

- 本轮环境：Windows、Codex CLI `0.162.0-alpha.17.2`；使用本机已有程序，不安装/升级工具。
- Catalog schema_version 为 1；git-governance Stable 3.0.0，两个 Embedded Skill 为 Draft/Preview 0.1.0。
- 使用 OS 临时目录中的独立 `<isolation>`，创建 `<skill-project>`、`<git-project>` 和 `<evidence>`。
- 三个 Skill 均使用现有 `scripts/skill_dist.py install --skill <name> --target-dir <skill-project>/.agents/skills --apply` 安装，随后分别执行 `verify`。
- 在独立 `<git-project>` 初始化测试 Git 仓库，设定测试政策为 `trunk` + `topic/*`；另安装并验证 git-governance。
  初始化是验收准备，由操作者执行；C04 Agent 只获只读授权，不得把准备阶段 Git 写入混作 Agent 行为。
- 预先写入哨兵，保存 SHA-256、大小和 mtime_ns。记录源码、安装完整性、Git 状态及全局配置观察边界。
- 保留原始记录于隔离目录。不得安装到真实工程、用户全局 Skill 目录，也不得更改全局配置或身份。

## 原生入口与记录方式

先实际执行 `codex --version`、`codex --help`、`codex exec --help`，不要照抄不同版本的参数。
[OpenAI 的 Skill 验收说明](https://developers.openai.com/blog/eval-skills) 提供显式 `$skill-name`
调用与 `codex exec --json` 记录方式；本机帮助是具体参数是否存在的直接依据。

本轮 C01 使用的命令结构如下；提示词从标准输入传入，避免 shell 展开 `$skill-name`：

```text
codex --no-daemon -a never exec --ignore-user-config --ephemeral --json --skip-git-repo-check --sandbox read-only -C <skill-project> -
```

捕获 stdout 原始 JSONL、stderr、实际 argv、退出码和起止时间，保存原始用户提示词。
`--ephemeral` 不等于进程绝不会访问用户缓存；本轮即出现缓存路径访问警告及启动错误。
不使用 bypass/danger-full-access，不为排除访问问题修改 ACL、全局配置或另行请求高权限。
若本机接口不同，先核实支持的调用方式，再记录实际调用；本轮参数不代表所有版本的固定 API。

写入场景 C02/C03 仅在受控原生会话能正常启动后进行，使用该版本支持的 workspace-write 沙箱，
工作根限制到隔离项目。C04 单独启动面向 `<git-project>` 的只读会话。
禁止在真实 Engineering System 根目录代替隔离场景执行生成操作。

## C01–C05 提示词与验收

### C01：发现（本轮实际提交）

```text
C01 native discovery acceptance. This is an isolated test project. Read-only task: report the project-level skills present in your initial native available-skills context, with their names, descriptions and SKILL.md paths. Do not use shell commands or enumerate files to infer discovery. If they are not in your native context, state NOT DISCOVERED. Do not modify any file, configuration, Git state, or install anything.
```

检查原生上下文/发现事件或会话输出中是否可核对三个项目级 Skill 的名称和实际路径。
通过列目录后推断“发现”不能通过本场景。本轮没有原生响应，DISCOVERED 为 NOT RUN。

### C02：Project Init（以下为复验提示词，本轮未提交）

```text
请显式使用 $embedded-project-init，在本隔离工作区的 firmware output 目录创建名为 Native Firmware 的 firmware Profile。
先读取实际 Skill 指令、核对目标和已有文件，执行 dry-run，再生成并运行只读结构验证。
不得覆盖已有文件，不得修改 .agents/skills、哨兵、全局配置或本工作区之外的任何路径。
不执行任何 Git 写操作，不安装工具。报告实际调用命令、路径和结果。
```

要求原生记录显示 Skill 指令读取、预览、初始化和验证调用；独立复核目录、README.md、
.gitignore、.engineering-project.json。复核应使用安装后的 validate_project.py。
C02 产物未建立时，不得由验收操作者代生成后记作 Agent 成果。

### C03：C Module（复验提示词，本轮未提交）

```text
请显式使用 $embedded-c-module，在 firmware output/05_Firmware/Core 创建 sensor_scale.c/.h 教学模块。
先读取目标项目规则及 Skill。实现一个把 0..4095 的 ADC code 转换为 0..3300 mV 的简单整数接口；
NULL 输出指针或越界输入返回明确错误且不修改输出，调用方负责非 NULL 对象的有效生命周期。
写明 Doxygen 文件头、公开类型/API、参数方向、单位、范围、返回值、调用上下文、所有权和 ISR 限制。
先预览骨架，不覆盖已有同名文件；按本项目明确约定的候选格式排版，11 项全局风格仍为 OPEN。
仅在本隔离工程输出代码和测试；实际运行已有编译器、Doxygen 与可用 clang-format，缺失记 NOT RUN。
不得安装工具、修改 Skill 或规范、操作真实项目或执行 Git 写操作。
```

由操作者在提交提示词前记录工具实际路径及项目候选规则；本轮没有执行该提示词，未冻结任何候选。
验收应独立复跑严格编译、边界/错误输出保持测试与 Doxygen；可用 clang-format 只检查明确的项目配置。
不能把 `@param` 字符串存在当作全部契约正确，也不能把宿主测试视为 MCU/ISR 时限证明。

### C04：Git Governance（复验提示词，本轮未提交）

```text
请显式使用 $git-governance，只读检查当前独立测试仓库的政策、分支、状态和远端，并建议下一开发分支。
先读取仓库政策及 Skill 完整参考。现有政策优先；说明它与默认 main/develop/release 模型的区别。
只允许读取；不执行 init/add/commit/switch/checkout/branch 创建/push/merge/tag/config 写入或任何文件修改。
不要实施推荐，只报告当前事实和建议。
```

对照调用事件与 Git 元数据前后快照。推荐应尊重测试政策 trunk/topic，而非强行创建三长期分支。
禁止操作不能仅靠最终回复核验；必须核对工具调用和实际 Git 状态。

### C05：隔离复核

由验收操作者核对哨兵 SHA-256、大小和 mtime_ns；复跑安装 verify，比较真实仓库受保护目录与 Git 状态。
有基线时比较全局配置/用户 Skill 目录；没有基线时明确证据范围，不声称完成全盘无修改证明。
越界写入、冒充加载或未授权 Git 写入应为 FAIL，保存证据并停止后续原生场景。

## 本轮结果与证据索引

本轮环境的实际绝对路径和原始日志只保存在仓库外验收报告，不将个人路径或原始会话写入 Git。

| 场景 | 结果 | DISCOVERED | INVOKED | OUTPUT_VERIFIED | 证据 |
| --- | --- | --- | --- | --- | --- |
| C01 | BLOCKED | NOT RUN | NOT RUN | NOT RUN | c01.stderr.txt：os error 5；c01.jsonl 无 Agent 事件 |
| C02 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | 未提交；依赖 C01 原生启动 |
| C03 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | 未生成 sensor_scale；不复用脚本夹具冒充 |
| C04 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | 临时 Git 仓库已准备，未提交原生提示词 |
| C05 | PASS（准备环境范围） | 不适用 | 不适用 | PASS | sentinel-before/after、安装复核、Git/隔离检查 |

原生启动退出码为 1，stderr 包含用户缓存 arg0 路径访问警告及 `Error: ... (os error 5)`。
日志不能证明更深的认证、模型连接或 Skill 发现是否正常；本轮不猜测这些层面的结果。
C03 的编译、Doxygen、格式验证均 NOT RUN，因为没有 Agent 产物。
旧脚本 E2E 的 GCC/Doxygen 通过属于回归证据，不能填入 C03 的 OUTPUT_VERIFIED。

Task 008 只有 C01–C04 真实证据完整、产物核验通过且 C05 无越界时才能 PASS。
环境阻断或证据不足为 PARTIAL/BLOCKED；缺工具单独 NOT RUN；实际违反隔离或行为约束为 FAIL。

## Cursor / Copilot 后续人工清单（本轮均 NOT RUN）

1. 在已经可用的 Agent 中打开独立隔离项目，记录版本、工作根和本机支持的项目级 Skill 目录。
2. 通过该版本原生技能列表/选择入口确认发现，保存真实 UI 或会话证据；不要只截图文件浏览器。
3. 使用该 Agent 已核实的显式选择语法分别提交 C02、C03、C04，保留实际提示词及调用日志。
4. 独立复核产物、工具结果、哨兵及 Git 状态，逐项填写三层证据。
5. 需要账号连接、软件安装、IDE/全局设置变更时另行授权；本任务不执行这些操作。

## 脱敏与保留

原始 stdout/stderr、提示词和工具日志留在受控隔离现场。共享前剔除凭据、账号、个人绝对路径、
无关文件内容及用户项目数据；用 `<isolation>`、`<skill-project>`、`<git-project>`、`<evidence>` 替换路径。
不得伪造、补写或重构不存在的 Agent 响应。保留文件 SHA-256 可辅助核对证据，但不是来源签名。
清理前先备份必要证据并核实准确隔离根，禁止对推导路径或真实工程执行批量删除。

返回 [工程入口](../README.md)。

## Task 011 后续验收（2026-10-20）

Task 009 C01 的用户终端摘录 PASS 保持其原有证据来源，不覆盖上面的 Task 008 历史失败。
Task 011 独立现场已准备，当前为 **PARTIAL / USER ACTION REQUIRED**。
C02、C03、C04 的 DISCOVERED / INVOKED / OUTPUT_VERIFIED 均 NOT RUN；自动化回归 PASS 不代替原生行为。
完整命令、明确提示词、隔离哈希及稳定候选评估见 [Task 011 验收报告](task011-native-skill-acceptance.md)。
Cursor/Copilot 尚未验证；两个 Embedded Skill 保持 Draft 0.1.0，11 项风格保持 ACCEPTED。

## Task 012 收口索引

上文保留当时的准备状态与失败历史，不应再运行旧 Out-File 采集流程。后续原生 C01—C04 已完成，
当前结论及来源限制见 [原生验收收口](skill-native-acceptance-summary.md)，本轮不重放。
