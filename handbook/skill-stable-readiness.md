# Skill 稳定候选评审

日期：2026-10-20。范围为 Codex 与已测本地工具链。评估不是 Stable 升级授权。

| 维度 | embedded-c-module | embedded-project-init |
| --- | --- | --- |
| 当前状态 | Draft / Preview 0.1.0 | Draft / Preview 0.1.0 |
| 总体评估 | **READY_WITH_LIMITATIONS** | **READY_WITH_LIMITATIONS** |
| 规格/文档 | frontmatter、相对链接、规范/模板同步 PASS | frontmatter、三 Profile 与分发同步 PASS |
| 安全/幂等 | dry-run、防覆盖、路径边界 PASS，重复生成拒绝覆盖 | dry-run、UNCHANGED、冲突保留、路径与 Junction PASS |
| 原生行为 | C03 读取、生成、业务 API 与独立验证 PASS | C02 firmware 初始化、重复执行 PASS；原 JSONL 历史 FAIL |
| 工具链 | 骨架和 ADC 示例 GCC C99/C11、格式、Doxygen PASS | 单测覆盖三个 Profile；独立 firmware 实测 PASS |
| 分发 | 两次 ZIP 字节一致，install/verify/upgrade/remove PASS | 同左；内容变化升级及故障恢复有隔离单测 |
| 独立性 | Python -I -B 仓库外执行；源不可用测试 PASS | 同左 |
| 项目规则 | 11 项 ACCEPTED 值、项目覆盖说明与分发副本一致性 PASS | 初始化不批准编码风格，目标项目规则优先 |
| 多 Agent | Codex 有证据；Cursor/Copilot NOT RUN | 同左；不泛化为三个 Profile 均有原生验收 |

## 发布前限制与动作

- 所有者分别批准 Stable 范围、版本和兼容承诺，不能仅更改 draft 字段。
- Windows 两项 symlink 测试因 WinError 1314 为 NOT RUN，Junction 已通过；发布前在具备权限的平台完成对应测试。远端 CI 未 Push，为 NOT RUN。
- Project Init 的原始 C02 日志缺陷须长期披露；若批准门禁要求完整原始流，需另行授权补验，不能修改旧证据。
- C Module 验证只覆盖所测骨架、示例与原生样例，不保证任意业务逻辑、MCU/ISR、RTOS、硬实时或 MISRA 合规。
- Cursor/Copilot 若进入原生支持承诺，须完成真实调用；格式兼容不是行为证据。
- 分发普通失败恢复已测；断电、强杀或恶意并发的原子性不作保证。

没有发现需要修改分发 API 的可复现缺陷；未修改 Skill、标准、模板及工具。
见 [原生索引](skill-native-acceptance-summary.md)、[实测记录](release-candidate-notes.md)、[发布门禁](release-candidate-checklist.md)。
