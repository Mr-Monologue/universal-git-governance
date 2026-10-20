# Task 010 验收记录

日期：2026-10-20。工作仓库：`G:\Engineering System`。
所有者在本对话明确批准“全部 11 项”，并分别授权 Task 009 证据提交、Squash 到 develop、Task 010 分支及本地提交。
风格冻结完成；没有稳定版发布授权，规范仍为 Draft 0.1.0，两个 Embedded Skill 仍为 Draft / Preview 0.1.0。

## 前置与证据

- Task 009 原 HEAD：`f317dffddb7fdae8f260527c2c4e80fc8fd9a898`，开始时工作区干净。
- 证据文档提交：`aa827314c4f59e8a0f891d0b57486ab467d8c6d8`。
- develop 本地 Squash：`6e67f9df2ee738a9933fbe9e83ddcb3af4029750`；暂存树与已验证 Task 009 树一致。
- Task 010 分支：`feature/embedded-c-style-freeze`，从上述 develop 派生。
- [C01 用户终端摘录](task009-c01-user-supplied-evidence.md)及[来源说明](native-agent-skill-recovery.md)：
  Session ID `01a154cd-b23a-7961-9658-245eba557ed1`。原生发现依据该会话 Skills 清单的摘录；
  正文读取依据三个 READ_STATUS: OK 与 Get-Content/Unicode 输出记录；不是用本轮文件列表代替原生发现。
  本轮也只读查看了隔离目录三个 SKILL.md，版本与约束相符，但该查看不等于重放原生会话。
- C01 PASS（用户提供的终端日志摘录）；未获取原始 jsonl，任务书第 2.3 节不强制原始 jsonl。
  C02–C04 及人工执行后的 C05 仍 NOT RUN，Task 009 整体 PARTIAL。

## 11 项批准结果

以下每项均从 OPEN / PROPOSED 转为 ACCEPTED / DEFAULT，来源为上述用户批准。
本表为验收时快照；现行规则唯一维护源为[规范正文第 16 节](../standards/embedded-c/C_CODING_STANDARD.md)。

| ID | 已批准默认值 | 项目覆盖与例外 |
| --- | --- | --- |
| C-STYLE-01 | Attach / K&R：函数和控制结构左括号同行 | 已有项目风格优先；不做无关重排 |
| C-STYLE-02 | 4 个空格；不使用制表符缩进 | 项目批准的 .clang-format 执行 |
| C-STYLE-03 | 100 列软限制 | 项目可选 80/120；不机械拆分字符串、宏和链接 |
| C-STYLE-04 | snake_case；公开函数/符号使用模块前缀 | 不普遍强制 g_/p_/pf_；保留已有 ABI |
| C-STYLE-05 | 类型用语义化名称，不普遍使用 _t；宏及枚举常量 UPPER_SNAKE_CASE | 第三方 API、RTOS 和已有类型约定优先；避免保留命名空间 |
| C-STYLE-06 | 新项目建议 C11；兼容已有 C99；C23 单独验证 | 目标工具链和项目安全认证要求优先 |
| C-STYLE-07 | 文件/API 必须 Doxygen；个人中文项目默认中文 | 团队/国际项目可用英文；标识符建议英文，参数名与代码一致 |
| C-STYLE-08 | 变更范围内执行可用格式检查、编译告警、公开 API Doxygen 校验和相关测试 | 缺工具报告 NOT RUN；项目可提高门禁 |
| C-STYLE-09 | 不默认宣称 MISRA 合规 | 项目选定标准版本、风险等级和偏离流程 |
| C-STYLE-10 | 默认 variable == constant；不强制 Yoda 条件 | 静态检查、团队约定和可读性优先 |
| C-STYLE-11 | @file、@brief 和真实版权/许可证；历史使用 Git/Changelog | 不伪造作者、日期；不强制冗长文件历史表；许可证须有实际依据 |

Doxygen 强制、真实参数契约及 volatile 不能替代同步的要求不变。
保留原 Checklist 对照和历史技术权衡，历史语句明确标注 Task 006 时点。

## 实现与兼容性

- 更新规范正文、决策历史、评审与审查清单及各级 README；不修改 ADC 算法。
- 配置保持 Attach、4 空格、Never Tab、100 列，并关闭机械拆分长字符串。
- 使用既有同步脚本分发文档及默认格式配置，共 8 份副本；独立 Skill 无需访问源码仓库。
- C/H 骨架现有内容已符合批准值，生成器无业务函数，不引入虚假 API、作者或许可证；模板与 CLI 保持原样。
- 新测试逐项检查默认值与对应例外、实际格式变换、独立副本规则漂移，并解析真实 Doxygen XML 的参数与返回契约。
- 既有 CI 的 unittest discover 自动纳入新增测试；工具按 PATH 或 CLANG_FORMAT / DOXYGEN 环境变量选择。
  缺工具会显式跳过并报告 NOT RUN。本轮未触发远端 CI。
- Git Governance、Project Init Skill、工程模板、Catalog 与 skill_dist.py 均与 develop 无差异。
  三个 Skill 的版本/发布状态不变，无真实业务项目安装，无全局配置改动。

## 实际验证

本轮最终使用 Python UTF-8 模式；CLANG_FORMAT 指向已有 F:/clang-format.exe，
DOXYGEN 指向已有 F:/Doxygen/doxygen/bin/doxygen.exe，仅作用于测试进程环境。

| 检查 | 结果 |
| --- | --- |
| Task 009 集成前 8 个验证入口 | PASS |
| Task 009 集成前 unittest | 95 项：93 PASS、0 FAIL、2 NOT RUN |
| Task 010 8 个验证入口 | PASS |
| Skill Creator quick_validate（-X utf8） | PASS |
| Task 010 最终 unittest | 100 项：98 PASS、0 FAIL、2 NOT RUN（36.998 秒） |
| Skill E2E，含真实编译/Doxygen | 15 PASS、0 FAIL、3 NOT RUN（本轮原生 Codex/Cursor/Copilot 调用） |
| GCC 13.1.0，ADC C99/C11 严格告警编译与边界测试 | PASS |
| 12 组 C99/C11 × 80/100/120 × Attach/Allman 对照编译与行为测试 | PASS |
| clang-format 20.1.1 示例 dry-run --Werror、生成骨架及长字符串 | PASS |
| Doxygen 1.12.0 完整 HTML/XML 告警门禁与参数/返回 XML 断言 | PASS |
| 独立生成、Dry Run、重复执行、防覆盖、安全回滚和打包 | PASS，单元测试及 E2E 覆盖 |
| Windows 原生 symlink 两项 | NOT RUN，WinError 1314；实际 Junction 测试 PASS |
| Clang 编译器 | NOT RUN，PATH 未找到；使用 GCC |
| C23、MCU 实时性、MISRA 认证、远端 CI | NOT RUN，不属于本轮实际验证 |

8 个入口：validate.py、validate_repository.py、validate_embedded_c.py、sync_embedded_c_skill.py --check、
validate_embedded_c_skill.py、sync_embedded_project_skill.py --check、validate_embedded_project_skill.py、validate_skill_distribution.py。
全量命令：`.venv/Scripts/python.exe -X utf8 -m unittest discover -s tests -v`。
E2E 命令：`.venv/Scripts/python.exe -X utf8 scripts/validate_skill_e2e.py --doxygen F:/Doxygen/doxygen/bin/doxygen.exe --keep-temp`。

### 失败与修复记录

- 初次受限环境 unittest 出现错误且未完成，已中止，不计 PASS；随后在获准的隔离临时目录测试上下文完成全量回归。
- 新增长字符串测试最初 FAIL，确认 LLVM 默认拆分字符串；补充 BreakStringLiterals=false 后 PASS。
- quick_validate 默认 GBK 解码失败；仅对命令使用 Python -X utf8 后 PASS，不改全局编码设置。
- ADC Doxygen 初次 XML-only 输出报告参数/返回缺失，实际源码含完整注释。
  改用 HTML+XML 完整输出后相同警告门禁 PASS；新增 XML 内容断言确认所有四个参数和两个返回状态。
  未删除文档、关闭告警或修改 ADC 实现来隐藏错误，原失败记录保留。

### 仓库外可复核记录

- E2E：`C:\Users\ryan\AppData\Local\Temp\skill e2e x2mq5yif\report.json`（包括命令、退出码与输出）。
- 编译/格式/初次 Doxygen：`C:\Users\ryan\AppData\Local\Temp\Task010-validation-ig64eny5\results.json`。
- Doxygen 完整输出复核：同目录 `Doxyfile-html`、`doxygen-html-result.json` 与 `doxygen/`。
- 临时记录可能被系统清理；回归测试可重跑。原生用户证据已归档在仓库内，不宣称获得原始会话文件。

## 实际变更文件

Task 009 的证据归档单独提交。本 Task 010 文件如下：

```text
README.md
handbook/task010-style-freeze-acceptance.md
scripts/sync_embedded_c_skill.py
scripts/validate_embedded_c.py
scripts/validate_embedded_c_skill.py
scripts/validate_skill_e2e.py
skills/README.md
skills/embedded-c-module/README.md
skills/embedded-c-module/SKILL.md
skills/embedded-c-module/references/C_CODING_STANDARD.md
skills/embedded-c-module/references/OPEN_DECISIONS.md
skills/embedded-c-module/references/REVIEW_CHECKLIST.md
skills/embedded-c-module/references/STYLE_DECISION_REVIEW.md
skills/embedded-c-module/references/config/.clang-format
skills/embedded-c-module/references/examples/style-review/README.md
standards/README.md
standards/embedded-c/C_CODING_STANDARD.md
standards/embedded-c/OPEN_DECISIONS.md
standards/embedded-c/README.md
standards/embedded-c/REVIEW_CHECKLIST.md
standards/embedded-c/STYLE_DECISION_REVIEW.md
standards/embedded-c/config/.clang-format
standards/embedded-c/examples/style-review/README.md
tests/test_embedded_c_freeze.py
tests/test_embedded_c_skill.py
tests/test_validate_embedded_c.py
```

提交前核对显式暂存文件清单、完整差异及 diff --check，保持真实 Git 作者身份。
本报告随 Task 010 单次本地中文提交保存，提交 SHA 以最终回复和 git log -1 为准（避免自引用 SHA）。
不 Push、不合并 Task 010、不创建 Tag/Release；完成后停止。
