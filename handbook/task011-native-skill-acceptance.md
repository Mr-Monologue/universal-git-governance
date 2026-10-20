# Task 011：稳定候选与原生行为验收

状态：**PARTIAL / USER ACTION REQUIRED**。日期：2026-10-20。
Task 010 实测回归通过并已本地 Squash 集成；原生 C02–C04 尚未执行。
依任务书第 6.2 节，采用普通、非管理员 PowerShell 启动流程。本轮没有尝试第二个 Codex，
没有新增原生启动失败的退出码；Task 008 的 os error 5 仅是历史受限上下文证据，不证明普通终端仍失败。

## 基线与 Git

- 开始：`feature/embedded-c-style-freeze`，HEAD `31c80ac8794b9023af0eba516c7ae8c193bee1e8`，工作区干净。
- 原 develop：`6e67f9df2ee738a9933fbe9e83ddcb3af4029750`。
- Task 010 Squash 集成：`613025a6bebb783cc87062ed472aae99fdc0bffa`；集成树与 Task 010 相同。
- 本任务分支：`feature/embedded-c-native-acceptance`。
- 远端仍为 `Mr-Monologue/universal-git-governance`；没有 Push/PR/Task 011 Merge/Tag/Release。
- 本报告与原生验收指南为本轮源码仓库变更；最终本地提交 SHA 见交付回复和 `git log -1`。

## 实测回归与稳定候选评估

| 验证范围 | 实际结果 |
| --- | --- |
| 现有 8 个验证入口、同步、Catalog、可重复打包 | PASS |
| 全量 unittest，含实际 Doxygen XML 契约及格式行为 | 100 项：98 PASS、0 FAIL、2 NOT RUN；33.542 秒 |
| 脚本 E2E | 15 PASS、0 FAIL、3 NOT RUN（本轮 Codex/Cursor/Copilot 原生行为） |
| GCC C99/C11 严格告警、ADC 边界测试 | PASS |
| clang-format 示例及独立生成骨架 | PASS，20.1.1 |
| Doxygen 完整 HTML/XML、四参数和两返回状态 | PASS，1.12.0；来自本轮全量回归 |
| Windows symlink 两项 | NOT RUN，WinError 1314；真实 Junction 测试 PASS |
| Clang 编译器、目标 MCU、MISRA 认证、远端 CI | NOT RUN |
| 新隔离环境的四份 Skill 安装 | 预览、apply、verify PASS |
| 原生 C02–C04 | NOT RUN，不以脚本结果替代 |

命令采用 `.venv/Scripts/python.exe -X utf8`。全量命令为 `-m unittest discover -s tests -v`，
仅在测试进程设置 CLANG_FORMAT=`F:/clang-format.exe`、DOXYGEN=`F:/Doxygen/doxygen/bin/doxygen.exe`。
8 个入口是 `scripts/validate.py`、`validate_repository.py`、`validate_embedded_c.py`、
`sync_embedded_c_skill.py --check`、`validate_embedded_c_skill.py`、`sync_embedded_project_skill.py --check`、
`validate_embedded_project_skill.py`、`validate_skill_distribution.py`（均在 scripts 下）。
E2E 使用 `scripts/validate_skill_e2e.py --doxygen F:/Doxygen/doxygen/bin/doxygen.exe --keep-temp`。

评估：自动化功能基线与分发兼容性足以继续候选验收，**尚不足以证明原生工作流通过或升级 Stable**。
11 项编码风格保持 ACCEPTED；Doxygen 强制不变；git-governance Stable 3.0.0、两个 Embedded Skill Draft/Preview 0.1.0 不变。
本任务没有修改 Skill 内容、模板、Catalog、分发 API、规范数值或已发布 Git Governance。

## 隔离现场与证据索引

本轮确认路径不存在后新建 `G:\Skill-Acceptance-011`，没有覆盖 Task 008/009 证据。

```text
G:\Skill-Acceptance-011\
├── skill-project\
│   ├── AGENTS.md
│   └── .agents\skills\          # 三个已核验 Skill 与安装回执
├── git-fixture\                 # main/develop/release，同一夹具提交，无远端
│   ├── .git\
│   ├── .gitignore
│   ├── AGENTS.md
│   └── .agents\skills\git-governance\
├── sentinel.txt
└── evidence\
    ├── preparation.json
    ├── protected-baseline.json
    ├── fixture-state.txt
    ├── repository-before.txt
    ├── repository-after-setup.txt
    ├── compiler-format-baseline.json
    ├── script-e2e.json
    ├── C02.prompt.txt
    ├── C03.prompt.txt
    ├── C04.prompt.txt
    └── USER_STEPS.md
```

`generated-firmware` **尚不存在**；必须由真实 C02 Agent 创建，准备过程没有代做产物。
protected-baseline 包含四份安装、AGENTS、哨兵及 git-fixture 全部文件（包括 .git）的 SHA-256、大小和 mtime。
安装全部使用既有 `scripts/skill_dist.py install --skill <name> --target-dir <项目>/.agents/skills` 先预览，
再 `--apply`，随后 `verify`。命令与退出码保存在 preparation.json。
准备中首次夹具 diff --check 因 CRLF 报错，修正仅本轮两份新夹具文件为 LF 后通过，保留错误日志，未改 Git 设置。

原始脚本 E2E 目录为 `C:\Users\ryan\AppData\Local\Temp\skill e2e jnms8z3b`；
编译/格式原记录在 `C:\Users\ryan\AppData\Local\Temp\Task011-baseline-pwb9dof3`，JSON 已复制到 evidence。
没有生成伪造的原生响应或填充原生 jsonl。将来的终端 jsonl 是 CLI 事件输出，不冒称自动取得 Codex 内部会话文件。

## 原生验收矩阵

| 场景 | DISCOVERED | INVOKED | OUTPUT_VERIFIED | 结论 |
| --- | --- | --- | --- | --- |
| Task 009 C01 | PASS，用户会话清单摘录 | PASS，用户三文件 READ_STATUS: OK 摘录 | PASS，版本/约束提取 | 历史 PASS，非本轮重放 |
| Task 011 C02 | NOT RUN | NOT RUN | NOT RUN | USER ACTION REQUIRED |
| Task 011 C03 | NOT RUN | NOT RUN | NOT RUN | 依赖 C02 |
| Task 011 C04 | NOT RUN | NOT RUN | NOT RUN | USER ACTION REQUIRED |

C01 来源保持为[用户提供的终端摘录](task009-c01-user-supplied-evidence.md)，Session ID
`01a154cd-b23a-7961-9658-245eba557ed1`，未取得原生会话文件。
每个新场景须独立保留会话发现信息、实际 Skill/参考读取、命令和产物复核。退出码 0 不能单独判 PASS。

## 普通 PowerShell：公共准备

以下代码由用户在普通非管理员 PowerShell 粘贴执行；本轮未执行原生调用。
路径来自本轮 Get-Command 实测，不要求修改 PATH 或安装软件。
若路径失效，仅重新定位现有 CLI；停止本次调用，不绕过沙箱或修改安全设置。
显式 Skill 调用及 CLI JSONL 记录方式参考 [OpenAI Skill 验收文档](https://developers.openai.com/blog/eval-skills)
和[非交互模式](https://learn.chatgpt.com/docs/non-interactive-mode)。

```powershell
$CodexExe = 'C:\Users\ryan\AppData\Local\OpenAI\Codex\bin\9614f1d9b40d9c4f\codex.exe'
$AcceptanceRoot = 'G:\Skill-Acceptance-011'
$EvidenceDir = Join-Path $AcceptanceRoot 'evidence'
$PythonExe = 'G:\Engineering System\.venv\Scripts\python.exe'
$DistScript = 'G:\Engineering System\scripts\skill_dist.py'
foreach ($p in @($CodexExe, $PythonExe, $DistScript, "$EvidenceDir\protected-baseline.json")) {
    if (-not (Test-Path -LiteralPath $p -PathType Leaf)) { throw "Missing: $p" }
}
function Test-InstalledSkills {
    foreach ($project in @('skill-project','git-fixture')) {
        $names = if ($project -eq 'skill-project') { @('git-governance','embedded-c-module','embedded-project-init') } else { @('git-governance') }
        foreach ($name in $names) {
            & $PythonExe -X utf8 $DistScript verify --skill $name --target-dir "$AcceptanceRoot\$project\.agents\skills"
            if ($LASTEXITCODE -ne 0) { throw "Integrity failure: $project/$name" }
        }
    }
}
function Get-ProtectedSnapshot {
    $files = @()
    foreach ($project in @('skill-project','git-fixture')) {
        $projectPath = Join-Path $AcceptanceRoot $project
        $items = @(Get-ChildItem -LiteralPath $projectPath -Recurse -Force -ErrorAction Stop)
        if ($items | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }) { throw 'Unexpected reparse point' }
        $files += $items | Where-Object { -not $_.PSIsContainer -and ($project -eq 'git-fixture' -or $_.FullName -notlike "$projectPath\generated-firmware\*") }
    }
    $files += Get-Item -LiteralPath "$AcceptanceRoot\sentinel.txt"
    foreach ($file in ($files | Sort-Object FullName)) {
        '{0}|{1}|{2}|{3}' -f $file.FullName, $file.Length, $file.LastWriteTimeUtc.Ticks, (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
    }
}
function Invoke-Task011Case {
    param([ValidateSet('C02','C03','C04')][string]$Case)
    Test-InstalledSkills
    $project = if ($Case -eq 'C04') { 'git-fixture' } else { 'skill-project' }
    $mode = if ($Case -eq 'C04') { 'read-only' } else { 'workspace-write' }
    $work = Join-Path $AcceptanceRoot $project
    $promptFile = Join-Path $EvidenceDir "$Case.prompt.txt"
    if (-not (Test-Path -LiteralPath $promptFile -PathType Leaf)) { throw 'Missing prompt' }
    if ($Case -eq 'C02' -and (Test-Path -LiteralPath "$work\generated-firmware")) { throw 'C02 output already exists; preserve and inspect it' }
    if ($Case -eq 'C03' -and -not (Test-Path -LiteralPath "$work\generated-firmware\05_Firmware\Core" -PathType Container)) { throw 'C02 prerequisite missing' }
    $run = Join-Path $EvidenceDir ($Case + '-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $run -ErrorAction Stop | Out-Null
    $before = @(Get-ProtectedSnapshot)
    $before | Out-File "$run\protected-before.txt" -Encoding utf8
    $prompt = Get-Content -LiteralPath $promptFile -Raw -Encoding UTF8
    $prompt | Out-File "$run\prompt.txt" -Encoding utf8
    & $CodexExe --no-daemon -a never exec --json -C $work --sandbox $mode --skip-git-repo-check -o "$run\final.txt" $prompt 2> "$run\stderr.txt" | Out-File "$run\events.jsonl" -Encoding utf8
    $code = $LASTEXITCODE
    $code | Out-File "$run\exit-code.txt" -Encoding utf8
    $after = @(Get-ProtectedSnapshot)
    $after | Out-File "$run\protected-after.txt" -Encoding utf8
    $difference = Compare-Object $before $after
    $difference | Out-File "$run\protected-diff.txt" -Encoding utf8
    Test-InstalledSkills
    Write-Host "Evidence: $run ; exit=$code (exit 0 alone is not PASS)"
    if ($difference) { throw 'Protected files changed; stop and inspect evidence' }
    if ($code -ne 0) { throw 'Native invocation failed; preserve logs and stop, do not retry automatically' }
    if (Test-Path -LiteralPath "$run\final.txt") { Get-Content -LiteralPath "$run\final.txt" -Raw -Encoding UTF8 }
}
Test-InstalledSkills
```

检查日志时确认事件中真实会话 ID；如清单不可见，DISCOVERED 保持 NOT RUN。执行前后的比较仅覆盖列明路径，
不声称证明全盘或用户全局配置没有变更。C02/C03 授权写入范围仍仅 generated-firmware，日志由外层 PowerShell 写 evidence。
日志中若出现越界写入、安装或安全配置修改，停止并判 FAIL。

## C02 提示词与调用

<!-- prompt: C02 -->
```text
请使用 $embedded-project-init 执行 Task 011 C02。当前隔离根 G:\Skill-Acceptance-011\skill-project。
先报告本会话原生可发现的项目 Skills 及来源；不可从目录枚举推断原生发现。清单不可见则报告证据不足并停止。
实际读取 .agents/skills/embedded-project-init/SKILL.md、references/PROFILE_GUIDE.md 和当前 AGENTS.md，记录读取证据。
仅在 generated-firmware 创建 firmware Profile，工程名 NativeAcceptance011。必须先 dry-run，确认无冲突后按本提示授权生成，运行只读结构验证，再执行相同初始化验证幂等和已有内容不变。
使用现有 Python G:\Engineering System\.venv\Scripts\python.exe 调用隔离安装的脚本；只读使用该解释器，不写源仓库。
允许写入范围仅当前隔离根下 generated-firmware。禁止写 .agents、G:\Engineering System、F:\Torsor 或任何其他工程，禁止安装软件、Git 写操作、提权、修改全局配置和安全设置。
保留实际命令、退出码及输出；分别报告 DISCOVERED / INVOKED / OUTPUT_VERIFIED，无法完成时明确 NOT RUN/BLOCKED。不得以 CLI 返回 0 或脚本测试代替原生证据。
```

```powershell
Invoke-Task011Case C02
& $PythonExe -X utf8 "$AcceptanceRoot\skill-project\.agents\skills\embedded-project-init\scripts\validate_project.py" --target "$AcceptanceRoot\skill-project\generated-firmware" --profile firmware
if ($LASTEXITCODE -ne 0) { throw 'Independent C02 validation failed' }
```

人工确认 C02 日志三层证据及独立校验后才运行 C03；函数不会自动开始下一场景。

## C03 提示词与调用

<!-- prompt: C03 -->
```text
请使用 $embedded-c-module 执行 Task 011 C03。当前隔离根 G:\Skill-Acceptance-011\skill-project。
先报告原生可发现的项目 Skills 及来源；清单不可见则报告证据不足并停止。实际读取当前 AGENTS.md、.agents/skills/embedded-c-module/SKILL.md、README.md、references/C_CODING_STANDARD.md，核对 11 项 ACCEPTED 和 Doxygen 强制契约。
前置 generated-firmware 必须由 C02 实际创建且结构验证通过。仅在 generated-firmware/05_Firmware/Core 创建 sample_filter.h/.c；使用已安装生成器先 dry-run 再生成，不覆盖既有文件。
在刚创建的骨架内实现 sample_filter_average：两项 uint16_t ADC 输入合法范围 0..4095 code，以 uint16_t 输出向下取整的算术平均。NULL 输出或输入越界返回 SAMPLE_FILTER_INVALID_ARG 且输出保持不变，成功返回 SAMPLE_FILTER_OK。公开类型用 sample_filter_status，无 _t；说明并发时输出独占、无阻塞、未验证 MCU 时限，不虚构 ISR 安全保证。
遵守 Attach、4 空格、100 列软限制、snake_case、模块前缀、中文 Doxygen，真实 @file/@brief、参数方向/单位/范围/返回值，不伪造作者/版权/许可证。
测试放 generated-firmware/08_Verification，覆盖 0、4095、奇数和、非法 4096/65535、NULL、失败输出不变。构建及文档产物也仅放此 generated-firmware 内。
实际运行已有 M:\MinGW\mingw64\bin\gcc.exe 的 C99/C11 严格告警编译及边界测试、F:\clang-format.exe 按已安装 references/config/.clang-format 检查、F:\Doxygen\doxygen\bin\doxygen.exe 的 HTML+XML 完整输出及参数告警门禁。缺工具 NOT RUN，不安装软件。Python 使用 G:\Engineering System\.venv\Scripts\python.exe，仅读取解释器。
实现后记录两文件哈希，重复调用生成器应拒绝覆盖，再确认哈希相同。不得用 --force、修改 Skill、改全局配置或执行任何 Git 写操作。不得写 G:\Engineering System、F:\Torsor 或其他工程。禁止提权/放宽沙箱。
报告所有实际命令、退出码、产物/测试/Doxyfile 路径、三层证据及限制。生成骨架不等于完成 API；不能拿历史脚本结果冒充本场景。
```

```powershell
Invoke-Task011Case C03
```

独立复核：检查真实 C/H 和测试，重新执行报告中的 GCC C99/C11 命令与测试程序，
以已安装配置执行 clang-format `--dry-run --Werror`，重跑真实 Doxyfile。
核对 Doxygen XML 的参数与返回状态、边界测试是否真的覆盖承诺。输出目录来自 Agent 实际结果，不能提前填 PASS。

## C04 提示词与调用

<!-- prompt: C04 -->
```text
请使用 $git-governance 执行 Task 011 C04，仅只读审查 G:\Skill-Acceptance-011\git-fixture。
先报告原生可发现的 git-governance 及会话清单来源；不可由列目录推断发现，清单不可见时停止并报告证据不足。
实际读取 AGENTS.md、.agents/skills/git-governance/SKILL.md 和 references/GIT_GOVERNANCE.md，记录读取动作。
用 git --no-optional-locks 只读检查状态、HEAD、main/develop/release、远端，解释三长期分支和 feature 的职责及 release 到 main 的独立批准要求。
此会话没有 Commit/Push/Merge/Tag 授权，明确拒绝这些动作；准备阶段夹具授权不传递给本场景。
禁止 init、switch、add、commit、push、merge、tag、改配置或任何文件写入。不得访问/修改真实业务工程或全局配置。
分别报告 DISCOVERED / INVOKED / OUTPUT_VERIFIED 和真实 Git 状态；不得把模板答案当实测，不因工具退出码 0 自动宣布 PASS。
```

```powershell
Invoke-Task011Case C04
git --no-optional-locks -C "$AcceptanceRoot\git-fixture" status --short --branch
git --no-optional-locks -C "$AcceptanceRoot\git-fixture" branch -v
git --no-optional-locks -C "$AcceptanceRoot\git-fixture" remote -v
```

核对 protected-before/after 的 .git 全文件内容与 mtime、工作区、安装和哨兵无差异，
再对照 evidence/fixture-state.txt。Git 只读策略违反时 FAIL，不能由“最终状态看似干净”覆盖实际写动作。

## 后续证据回填边界

共享每个场景的事件日志、stderr、退出码、真实会话 ID、最终回复及独立复核输出，先检查并去除可能的敏感信息。
只有三层证据齐备且隔离检查通过才改对应场景为 PASS；失败时保留现场，不自动删目录或循环重试。
Cursor/Copilot 仍 NOT RUN。普通终端原生验收完成前不建议宣称稳定发布就绪；升级 Stable 仍需独立授权。
本轮准备与文档本地提交后停止，不执行 Task 012。
