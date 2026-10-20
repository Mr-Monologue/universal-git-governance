# 发行准备记录与 Changelog 草案

日期：2026-10-20。仅 Task 012 准备，未发布、未批准 Stable/RC。
Task 011 来源 `64fed766f333fce6b6d9ac313031e9faab302366`；本地 Squash 集成
`7475b778e2ced15e717f7195998cf175ea9eaffd`，树一致。
Task 012 分支 `feature/skill-stable-candidate-prep`，最终文档提交见该分支 Git log。

## Unreleased：相对历史 v3.0.0

- 新增工程体系目录、Embedded C 标准、11 项已批准默认风格与强制 Doxygen。
- 新增 Draft C/H Module Skill、三 Profile Project Init Skill，可独立分发运行。
- 新增 Catalog、确定性打包、受管安装/校验/升级/安全移除、隔离回归。
- 已完成 Codex C01—C04 功能验收；本轮形成证据索引、稳定候选评审和版本/发行提案。
- Git Governance 3.0.0 目录、LICENSE 与历史 Tag 无差异，旧安装入口保留；不声称旧 Tag 包含新增模块。

## 本轮实测

| 入口/行为 | 结果 |
| --- | --- |
| validate.py / validate_repository.py / validate_embedded_c.py | PASS |
| sync_embedded_c_skill.py --check / validate_embedded_c_skill.py | PASS |
| sync_embedded_project_skill.py --check / validate_embedded_project_skill.py | PASS |
| validate_skill_distribution.py | PASS |
| unittest discover -s tests -v | 100 项：98 PASS、0 FAIL、2 NOT RUN |
| 三 Skill 双次 pack、顶层及 LICENSE、安装预览/apply/verify/重复安装 | PASS |
| 三 Skill upgrade 预览/apply、verify、remove 预览/apply | PASS；同源升级 UNCHANGED |
| 内容变化升级、故障恢复、保护其他安装 | PASS，test_skill_distribution 隔离源码夹具 |
| 源不可用后独立运行 | PASS，既有分发单测 |
| 本轮独立 firmware 初始化与 C/H 生成 | PASS，Python -I -B；拒绝覆盖退出 1 为预期 |
| 生成 C/H 及 ADC 示例 GCC C99/C11、严格告警、ADC 边界运行 | PASS |
| 已安装配置 clang-format / Doxygen HTML+XML 严格告警 | PASS |
| validate_skill_e2e.py，显式指定 GCC / Doxygen | 15 PASS、0 FAIL、3 NOT RUN（该脚本不执行原生 Agent） |
| 两项 Windows symlink | NOT RUN，WinError 1314；Junction PASS |
| 远端 CI、Cursor/Copilot 原生调用、MCU/ISR、MISRA | NOT RUN |

使用已有 GCC 13.1.0、clang-format 20.1.1、Doxygen 1.12.0；只设置测试进程工具路径。
首次受限执行因临时 stdout 日志写入 PermissionError 中止，未形成完整测试结论；
随后在授权新建隔离目录完整运行。环境错误不冒称 PASS。
脚本 E2E 覆盖 firmware/robotics 的独立生成、重复执行、防覆盖、路径安全和安装移除；
它的原生 NOT RUN 不覆盖历史原生 PASS。最终文档检查另执行 validate_repository.py 和 git diff --check。

## 本轮真实包清单（不是正式发布）

两次打包到不同目录，逐字节和 SHA-256 一致。包源为上述 develop 集成提交，Task 012 仅改文档。

| 文件 | SHA-256 |
| --- | --- |
| git-governance-3.0.0-stable.zip | `022d6012cd8ad4a7077d4d4f6b4ced46c1055f8359c2a6d5fba624fd49ad53ca` |
| embedded-c-module-0.1.0-preview.zip | `136a9b7fbd76fb9eeb1ce0e85baf77915e1a9f2158fc048d38034ddfde309479` |
| embedded-project-init-0.1.0-preview.zip | `642d598c8302e4790560f53029d0d5a91b16c383882a5cd201b0a224d2ee37b0` |

包、日志、构建产物仅保存在仓库外 Task 012 隔离现场；保留 baseline-results.json、
distribution-results.json、packages.json、逐命令 stdout/stderr。ZIP 顶层为各 Skill 名称，包含资源和 LICENSE。
不替换历史发行 ZIP。公开仓库只提交摘要，不提交原生日志/个人目录/构建文件。

## 安装与管理命令

从批准的仓库源码根目录运行，先读取 Catalog/--help。操作者自行指定已授权的隔离
`$target`（Skill 安装根）与 `$packages`（包输出）；不要将未指定变量的示例直接用于业务工程。
分发工具需 Python 3.11+、既有 PyYAML 6.0.3；安装后生成器仅需 Python 标准库。

```powershell
python scripts/skill_dist.py list
python scripts/skill_dist.py pack --skill embedded-c-module --output-dir "$packages"
python scripts/skill_dist.py install --skill embedded-c-module --target-dir "$target"
python scripts/skill_dist.py install --skill embedded-c-module --target-dir "$target" --apply
python scripts/skill_dist.py verify --skill embedded-c-module --target-dir "$target"
python scripts/skill_dist.py upgrade --skill embedded-c-module --target-dir "$target"
python scripts/skill_dist.py upgrade --skill embedded-c-module --target-dir "$target" --apply
python scripts/skill_dist.py verify --skill embedded-c-module --target-dir "$target"
python scripts/skill_dist.py remove --skill embedded-c-module --target-dir "$target"
python scripts/skill_dist.py remove --skill embedded-c-module --target-dir "$target" --apply
```

其他 Skill 替换名称即可。管理操作先预览再 apply；安装/升级读取仓库源码，不支持任意外部 ZIP。
旧 Git Governance 手动解压入口见 [README](../README.md)，无管理回执的手动安装不能自动接管。

## 失败恢复与回滚

1. 升级前 verify，备份完整旧 Skill 与 `.skill-dist/<name>.json`，保留旧源码/包/哈希并验证备份可读。
2. 未知修改、额外文件、回执缺失或事务残留均停止，备份现场；不 force、不删锁、不递归清理。
3. 无漂移的受管安装可在另行授权下用已验证旧源码执行 upgrade 预览/apply，再 verify；回退也是需授权的写入，不 reset 正式仓库。
4. 有事务残留时先核对错误路径中的旧目录/回执，在独立位置验证备份，再制定逐路径恢复。不能用 remove 删除用户改动以绕过保护。
5. 普通失败恢复有故障注入覆盖；强杀/断电不保证原子性。没有备份的文件不能假定可恢复。移除不删除项目产物或其他 Skill；手动安装沿用其备份与恢复方式。

两个 Skill 均 [READY_WITH_LIMITATIONS](skill-stable-readiness.md)，仍 Draft/Preview 0.1.0。
后续需逐项批准 [发布门禁](release-candidate-checklist.md)。本次无 Push/PR/Task 012 Merge/Tag/Release。
