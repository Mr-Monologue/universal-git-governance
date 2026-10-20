# 版本与 Release Manifest 提案

状态：**PROPOSAL / 待批准**，不是正式 Policy。本次不分配仓库正式版本。

Skill Version 与 Repository Release Version 独立。git-governance 保持 Stable 3.0.0，
两个 Embedded Skill 保持 Draft/Preview 0.1.0。未来按各自兼容性、输入输出和维护承诺独立定版；
版本和状态改变须单独批准，再同步 frontmatter、Catalog channel、文档及发行清单。

历史仓库 `v3.0.0` 是 Git Governance 基线，不追溯声称包含后来新增的工程体系模块。
下一聚合版本由所有者选择，不能从某个 Skill 数字推导；不移动旧 Tag、不替换旧 Release，
不擅自新增 Skill Tag 命名制度。

沿用 [Git Governance](../git-governance/references/GIT_GOVERNANCE.md)：feature 从 develop 派生，
指定候选进入固定 release，当次验证及单独授权后晋升 main。
RC `vX.Y.Z-rc.N` 与正式 `vX.Y.Z` 分开；Tag 是仓库级引用，不属于分支。
当前本地 release 不存在，只有 origin/release；本任务不创建它。

## Manifest 方案

[示例](release-manifest.example.json) 标注 example_only，占位值不代表真实发布。
正式清单需绑定实际仓库提交 SHA、批准版本、候选/正式状态、审批记录；逐 Skill 记录
版本/channel、源目录、安装相对位置、LICENSE、实际 ZIP 文件名/SHA-256、测试与 NOT RUN 项。
同时保留构建工具版本、原生证据摘要、支持范围和回滚旧包/回执。

从准确待发布提交打包两次，比较字节与 SHA-256；Manifest 只能填实算值。
同一仓库 Release 可以携带不同 Skill 版本。SHA-256 是完整性校验，不是签名/来源认证。
`scripts/skill_dist.py` install/upgrade 从验证后的仓库源码读取，不支持任意外部 ZIP 安装。

旧 Git Governance ZIP 顶层、LICENSE、路径与安装说明保持不变；新的确定性包无需与历史 ZIP
字节相同，不覆盖历史包。未来路径迁移须另立兼容计划，本提案不授权执行。
