# Agent Skill 隔离端到端验证

入口为 [validate_skill_e2e.py](../scripts/validate_skill_e2e.py)，回归测试见
[test_skill_e2e.py](../tests/test_skill_e2e.py)。仅验证现有三个 Skill 的组合流程，
不生成可交付的驱动或控制算法，不批准编码风格，不发布或安装到真实项目。

## 运行

从仓库根目录使用 Python 3.11+ 及已有 PyYAML 6.0.3 环境：

```powershell
python scripts/validate_skill_e2e.py --help
python scripts/validate_skill_e2e.py
python scripts/validate_skill_e2e.py --keep-temp --verbose
python -m unittest discover -s tests -v
```

默认通过 PATH 查找 GCC/Clang、Doxygen；缺失则明确 NOT RUN，不安装工具。
可用 `--compiler "已有编译器完整路径" --doxygen "已有工具完整路径"` 指定已安装工具。
显式指定的程序无法运行或返回错误时为 FAIL，不把配置错误当成缺失而跳过。
没有 `--target-dir` 参数，也不接受用户工程作为测试目标。

每次用 tempfile 创建仓库外带空格的 `skill e2e ...` 唯一目录；默认结束时清理，
普通中途失败也执行清理。`--keep-temp` 才保留现场，终端显示确切路径，
其中 `report.json` 记录每项结果、完整 argv、cwd、退出码、stdout/stderr。
`--verbose` 将命令证据同时输出到终端，便于 CI 留档；默认清理时 JSON 也随现场清理。
检查临时父目录，拒绝落在本仓库内；清理前验证确实是本次创建的根及其路径安全性。
发现链接/重解析点或清理失败时报告失败，保留现场人工复核；不递归清理调用者提供的路径。

## 验证链与真实 CLI

1. 对仓库 Skill、Catalog、规范和模板做内容快照，复制临时分发源码夹具。
2. 从 Catalog 验证三项来源、installable、Stable 3.0.0 / Draft 0.1.0。
3. 每个 Skill 用公开 CLI 打包两次，比较 ZIP 字节、SHA-256、条目结构及源码内容。
4. 安装到临时 `agent test project/.agents/skills/`，验证安装内容与包一致；
   检查 dry-run 零写入、verify 只读、重复安装 UNCHANGED 且文件时间戳不变。
5. 临时源码夹具改名至不可用位置，从已安装的两个 Skill 执行 Firmware 与 Robotics 场景。
6. 恢复夹具路径，注入安装篡改、同名文件、非法模块名、目录穿越，要求拒绝且零写入；
   检查安全移除只移除目标 Skill，保留其他安装和无关文件。
7. 复核源内容未改动和 11 项 OPEN/PROPOSED，按三层证据汇报。

管理 CLI 的真实用法如下。占位路径均由入口在本次临时目录中分配：

```text
python <fixture>/scripts/skill_dist.py list
python <fixture>/scripts/skill_dist.py pack --skill <name> --output-dir <packages>
python <fixture>/scripts/skill_dist.py install --skill <name> --target-dir <skills>
python <fixture>/scripts/skill_dist.py install --skill <name> --target-dir <skills> --apply
python <fixture>/scripts/skill_dist.py verify --skill <name> --target-dir <skills>
python <fixture>/scripts/skill_dist.py remove --skill <name> --target-dir <skills>
python <fixture>/scripts/skill_dist.py remove --skill <name> --target-dir <skills> --apply
```

现有安装器从已验证的源码安装，**不支持从 ZIP 安装**；本验证分别验证 ZIP、安装及二者内容一致，
不声称增加 ZIP 安装功能。复用既有管理工具，无升级版本或另建安装系统。
Git Governance 是文档型 Skill，本轮验证格式、分发、引用完整性和管理行为；不自动执行 Git 治理动作。

## 两个跨 Skill 场景

分别令 `<profile>` 为 `firmware`、`robotics`，`<project>` 为本次临时目录中的两个不同项目。
安装位置与生成项目都在同一个测试拥有的根下；使用已安装脚本绝对路径调用，
不假设 Agent 会跨项目自动发现它们。

```text
python -I -S -B -X utf8 <skills>/embedded-project-init/scripts/init_project.py --target <project> --name "E2E <profile>" --profile <profile> --dry-run
python -I -S -B -X utf8 <skills>/embedded-project-init/scripts/init_project.py --target <project> --name "E2E <profile>" --profile <profile>
python -I -S -B -X utf8 <skills>/embedded-c-module/scripts/new_c_module.py --module e2e_sample --output <project>/05_Firmware/Core --dry-run
python -I -S -B -X utf8 <skills>/embedded-c-module/scripts/new_c_module.py --module e2e_sample --output <project>/05_Firmware/Core
python -I -S -B -X utf8 <skills>/embedded-project-init/scripts/validate_project.py --target <project> --profile <profile>
```

验证 C/H 的 Doxygen 文件头、include guard、Draft 标记和模板展开；重复项目初始化不改写内容或文件时间戳，
重复模块生成必须失败且保持原文件，非法名字必须拒绝。Robotics 的 Motor、Mechanical、Hardware、Simulation
区域只允许目录/占位文件，不生成虚假 CAD、EDA、Maxwell 文件或实验结果。

生成器没有业务 API，不能声称验证了“自动生成的公开接口”。另从安装后的参考文档提取现有
`style_sample` 契约示例至单独临时夹具，检查 @param[in/out]、@retval、@pre、@note、mV 和 ISR 描述。
具备编译器时对骨架和契约夹具使用 C11、Wall/Wextra/Wpedantic/Wconversion/Wsign-conversion/Werror 编译。
具备 Doxygen 时生成临时文档并将文档告警视为错误。它们不证明所有权、单位或 ISR 时限承诺在实机上成立。
现有 Task 006 行为测试继续执行；本 E2E 不实现新的控制算法。

## 安全边界与失败恢复

路径与分发检查复用 [skill_dist_support.py](../scripts/skill_dist_support.py)。
E2E 入口在调用前检查输出位于本次拥有的根，拒绝目录穿越、根本身、外部目录及非目录祖先。
安装器和项目初始化器的 CLI 拒绝穿越，作为独立的负向场景验证。
**C 模块生成器自身没有目标根隔离策略**：本任务保持 Skill 内容不变，路径 containment 是 E2E 的保护层，
不能据此宣称直接调用该生成器会拒绝任意外部输出、`..` 或链接。真实使用仍须核对明确授权的路径。

隔离 Python 使用 `-I -S -B`，临时源码夹具不可用，验证生成器仅靠安装资源及标准库工作。
这不是 OS 沙箱，也没有撤销进程对真实仓库的读权限；不声称防御恶意 Skill 或并发攻击者。
源快照比较覆盖分发内容（排除缓存），最终 Git 检查另确认已跟踪 Skill 文件未变。

普通失败会停止依赖步骤并尝试清理；仅恢复测试自己注入的篡改，不能修复真实用户安装。
安装器部分写入、升级和移除回滚继续由 [既有分发测试](../tests/test_skill_distribution.py) 覆盖；
模块/项目生成失败回滚由既有 Skill 测试覆盖。本入口另测工作流中断清理及显式保留诊断，
不保证断电、强杀或恶意并发下的事务原子性。

## 证据与结果定义

| 层级 | 本入口可提供的证据 | 判定边界 |
| --- | --- | --- |
| 格式与分发 | YAML、资源、ZIP、受管安装、校验、幂等、安全移除 | 实际检查成功 PASS，断言/命令失败 FAIL |
| 独立执行 | 已安装脚本在外部项目组合运行、骨架/契约与可用工具检查 | 实际成功 PASS；工具缺失 NOT RUN |
| Agent 原生发现/调用 | Codex、Cursor、Copilot 真正加载并遵循 Skill | 本入口固定 NOT RUN，不能由读文件或脚本执行推断 |

当前没有本轮三个 Agent 原生加载的运行证据，需未来在受控会话中另行记录 Agent 版本、发现方式、
实际调用和结果。现有会话中助手阅读源码也不算新安装的原生发现。没有为此安装 Agent、插件或连接账号。

汇总按检查项计数，编译/Doxygen 各按 Profile 一项；不是子进程数量，也不与 unittest 数量相加。
有 FAIL 返回 1，否则返回 0；NOT RUN 始终单独保留，不转换为 PASS。
启用全部本机工具的已验证路径为 **15 PASS、0 FAIL、3 NOT RUN**，三项为原生 Agent。
缺编译器或 Doxygen 时各增加两项 NOT RUN。单元测试专门模拟工具缺失，验证不会虚报 PASS。

[现有 CI](../.github/workflows/validate.yml) 增加 `python scripts/validate_skill_e2e.py --verbose`，
保留全部旧检查和 unittest 自动发现；不修改旧 validate.py。远端 Actions 只有实际触发才有结果，
本任务未 Push，不能把本地通过写成远端 CI 通过。

返回 [工程入口](../README.md)；分发管理细节见 [分发手册](agent-skills-distribution.md)。
