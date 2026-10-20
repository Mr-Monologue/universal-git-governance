---
name: embedded-project-init
description: 为新建或明确授权补充骨架的嵌入式项目选择 firmware、embedded-fullstack 或 robotics Profile，预览并安全生成编号式目录和说明，执行只读结构验证。不用于迁移已有工程、生成 MCU/EDA 工程或执行 Git 初始化。
metadata:
  version: "0.1.0"
  status: "draft"
---

# Embedded Project Init · Draft / Preview

1. 确认用户明确给出的目标目录、项目显示名称及初始化授权，读取目标已有规范和文件。
   若需求不足以选择 Profile，询问范围；不得从工作目录猜测项目根，不访问无关工程。
2. 阅读 [Profile 指南](references/PROFILE_GUIDE.md)，按需求选择纯固件、软硬件/上位机或机电控制范围。
   数字为领域分类，不是阶段；仅 robotics 包含课程，不能因为编号缺失而重排已有目录。
3. 从本 Skill 目录调用 [生成器](scripts/init_project.py)，明确传入 target、name、profile，先使用 `--dry-run`。
   向用户说明将创建的目录和冲突；已有任务授权足以执行相符的生成，无需重复确认。
   冲突时停止，保留用户文件；不增加 force、自动合并或偷偷改目标路径。
4. 按相同参数实际生成，再用 [只读验证器](scripts/validate_project.py) 检查。
   链接、重解析点、越界或非目录对象被拒绝；异常时报告回滚与残留，不能自动清理已有内容。
5. 汇报实际路径、Profile、创建/UNCHANGED/CONFLICT、验证命令与 PASS / FAIL / NOT RUN。
   目录骨架不等于完成硬件或软件工程；不能声称实时性或安全合规。

本 Skill 不执行 Git init/add/commit/push、网络下载、软件安装、全局配置或跨项目操作。
Git 治理由目标项目既有治理与独立授权管理，使用本 Skill 无需先安装其他 Skill。
不生成虚假作者、版权、许可证、机密模板或特定 MCU/SDK 代码。
既有 Doxygen 强制要求仍有效；本次目录初始化不批准大括号、命名、行宽或 C 版本等待决风格。

用法、幂等与失败限制见 [README](README.md)。
