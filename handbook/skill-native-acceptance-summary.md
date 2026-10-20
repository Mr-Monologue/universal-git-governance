# Codex 原生验收收口

日期：2026-10-20。Task 012 只读复核既有材料，未重放 C01—C04。
Task 011 Codex 原生功能验收完成，不代表跨 Agent 兼容、Stable 或发布批准。
[Task 011 准备报告](task011-native-skill-acceptance.md) 保留当时 PARTIAL 状态；
旧 Out-File 采集命令仅为历史，不应再使用。后续采用 Python 二进制 stdout/stderr。

## 三层证据

VERIFIED 表示本次实际读取核对，USER_REPORTED 表示用户历史摘录，NOT_AVAILABLE 表示未取得底层资料。
相对证据标识以保管者的隔离现场为根，不是公开下载地址，不保证长期在线。

| 场景 | 核实状态 | DISCOVERED | INVOKED | OUTPUT_VERIFIED | 结论 |
| --- | --- | --- | --- | --- | --- |
| C01 | USER_REPORTED；摘录文本已读取，底层会话 NOT_AVAILABLE | 同会话清单摘录 | 三份 READ_STATUS: OK 摘录 | 版本/约束摘录 | 历史 PASS |
| C02 | VERIFIED：原 final、有效事件及独立记录 | 原 final 对同会话元数据的报告 | item_1/2 读取，item_3 dry-run，item_5 创建 | item_7 幂等复核；独立记录 17 目录/14 文件 | 功能 PASS；原 JSONL 完整性 FAIL |
| C03 | VERIFIED：31 条完整事件、产物报告与工具记录 | 原生最终答复报告项目清单 | item_6/7 预览与生成、规范读取 | item_11 工具链、边界、覆盖保护；74 文件快照一致 | PASS |
| C04 | VERIFIED：20 条完整事件与前后记录 | 第 19 条 item_9 报告预加载清单及来源 | 第 16 条 item_7 实际读取三个完整文件 | 第 10 条 item_3 只读 Git；281 文件快照一致 | PASS |

发现层来源是原生事件对 Available skills 和来源的明确报告，不是目录枚举。
未独立取得底层发现机制输入；调用与产物不单凭自述或退出码判定。
C04 Unicode 转义还原后与实际 AGENTS、SKILL、完整参考规范一致；Git 查询确认 main 干净、无远端，
main/develop/release 都为 `314a92b18b376cc422841ddaa67a1afec2150467`。
两次失败的编码处理尝试保留，后续成功不抹除失败记录。范围快照不等于全盘审计。

## 会话及证据定位

| 场景 | Session ID | 相对标识 |
| --- | --- | --- |
| C01 | `01a154cd-b23a-7961-9658-245eba557ed1` | [用户摘录](task009-c01-user-supplied-evidence.md) |
| C02 | `01a1599e-76aa-7ed0-bd70-eb7d783cfcff` | `evidence/C02-7a02ddb7bcde4c76aed6044a4af23609/` |
| C03 | `01a159be-abec-7582-9e05-cf6d20c35db7` | `evidence/Task011A/C03-6e1d8ad63e8c4ade8c0f62f2745628be/` |
| C04 | `01a159ce-c02e-7b91-a030-b8c3377c7833` | `evidence/C04-85b5be9df04a462184b17a6a292bca23/` |

原始 events.jsonl 实算 SHA-256：

| 场景 | SHA-256 | 完整性 |
| --- | --- | --- |
| C02 | `2e2ae0b9d18874d557a1ee1e07d13ebd23cf69a6cdff437cf592a93589423695` | 18 行，第 3、10、17 行损坏，FAIL |
| C03 | `5ebe9bb934543cac3c387aa76c58dcd390bb825909f34912eb70ae9ab4a585dc` | 31 行、0 坏行 |
| C04 | `d90807ceb2e097f80a97be83c6babd1ffb9832b061d851a881b5d5db46cff229` | 20 行、0 坏行 |

C02 补充材料是 `evidence/Task011A/c02-prerequisite.json`、`independent-structure.json`。
C03 工具结果是 `skill-project/generated-firmware/08_Verification/C03_REPORT.md`、`c03-results.json`。
原始 C02 未修复/覆盖；后续完整日志不能替代它。外层 CLI 事件流不冒称内部会话文件。
原始日志、用户名绝对路径和构建制品不进入本索引。
Cursor/Copilot、目标 MCU/ISR、MISRA 认证均 NOT RUN。C01 是冻结风格前历史，当前 11 项保持 ACCEPTED。
返回 [候选评审](skill-stable-readiness.md)。
