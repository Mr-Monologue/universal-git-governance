# GitHub Preview 发布与消费契约

Task 014 授权的聚合候选版本为 `v3.1.0-rc.1`，只允许 GitHub Pre-release。
本文件是发布前契约，不是远端发布成功证明；最终 PR、CI、提交和下载结果以交付报告及
GitHub 实际页面为准。main 不晋升，历史 v3.0.0 不修改。

| Skill | 独立版本 | 状态 | 资产 |
| --- | --- | --- | --- |
| git-governance | 3.0.0 | Stable | git-governance-3.0.0-stable.zip |
| embedded-c-module | 0.1.0 | Draft / Preview | embedded-c-module-0.1.0-preview.zip |
| embedded-project-init | 0.1.0 | Draft / Preview | embedded-project-init-0.1.0-preview.zip |

第四个资产 `packages.json` 绑定仓库版本、release_tag、实际 release_commit 及各 Skill 的
name/version/status/filename/sha256/size_bytes。三个 ZIP 顶层各为 Skill 名称，必须完整保留
SKILL.md、LICENSE、references、scripts 和模板等实际随包资源。源码 ZIP 不是 Skill 发行包。
仓库聚合版本不覆盖 Skill 独立版本，两个 Embedded Skill 不因发布 RC 变为 Stable。

## 发布门禁

先按治理规则将已完成内容通过 PR 集成远端 develop，CI 通过后再通过 PR 晋升固定 release。
在实际候选树执行全部校验、单测、E2E、双次打包及隔离验证；只有通过后才创建唯一 annotated RC Tag。
Tag 对应 CI 也须通过，随后创建非 Draft、prerelease=true 的 GitHub Release，上传完整四资产。
Tag 冲突、审批阻断、CI 失败均停止，不移动 Tag、不强推、不发布不完整候选。
发布后从匿名 HTTPS 下载再次验证，不用本地源码替代云端消费证据。

## 给 Agent 的自然语言安装请求

使用者可以请求：“请从本仓库 GitHub 的 v3.1.0-rc.1 Pre-release 下载三个 Skill 包及
packages.json，核对版本、字节数与 SHA-256，先检查目标项目现有规则和安装目录，
预览后仅在我授权的项目 `.agents/skills/` 安装完整目录，保留许可证并验证独立运行。
如目标已存在或发现冲突，停止，不覆盖、不修改全局配置，不自动提交或初始化工程。”

不要求使用者手动运行 CLI。执行 Agent 应检查实际公开资产链接与 Pre-release 标识，
以完整性清单校验下载，不把哈希称为数字签名或可信来源认证。
解压前拒绝绝对路径、`..`、反斜杠路径穿越、驱动器/设备名、符号链接及重复/冲突条目；
确认解析后的每个目标仍位于新建隔离暂存目录。完整解压并核验后，再按授权安装。
既有目标不可直接覆盖；不能只复制 SKILL.md。旧 Git Governance 安装方式继续有效。

现有 skill_dist.py 从仓库源码管理安装，不支持外部 ZIP 输入。云端 ZIP 安装采用经过校验的
完整目录复制；这不会自动创建受管安装回执，不得伪造 .skill-dist 记录或声称能直接受管升级/移除。
安装后的生成器使用 Python 3.11+ 标准库，脚本运行可加 -B 避免缓存；
Project Init 应先 dry-run 再生成并验证，C Module 先 dry-run、拒绝覆盖。

## 回滚与限制

安装前备份旧目录并记录清单；保留旧包及校验和。失败时保留现场，不删除用户新增内容。
仅在另行授权、核对精确文件清单后移除本次新安装并恢复已验证备份；
无备份不能承诺恢复，不批量清理未知文件，不改变历史 Tag。

Codex C01—C04 的历史结论见 [证据索引](skill-native-acceptance-summary.md)；
C02 原始 JSONL 损坏仍为历史 FAIL。Cursor/Copilot 原生调用未验证，需独立试点，
不能由公开下载或格式兼容推断原生发现成功。11 项 C 风格保持 ACCEPTED，Doxygen 强制。
Windows symlink 权限跳过须披露；远端 Linux 验证不能伪称 Windows 特权场景已测。
不保证 MCU/ISR/硬实时或 MISRA 合规。

本任务不访问或修改下游业务工程，不自动执行下游初始化或正式版发布。
