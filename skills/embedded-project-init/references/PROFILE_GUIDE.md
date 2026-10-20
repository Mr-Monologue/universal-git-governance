# Profile 选择指南

| Profile | 适用范围 | 增加的分类 |
| --- | --- | --- |
| [firmware](../assets/profiles/firmware.json) | 纯嵌入式固件 | 项目管理、参考、系统设计、固件、验证、工具 |
| [embedded-fullstack](../assets/profiles/embedded-fullstack.json) | 硬件加固件及上位机 | Hardware、Software、Bench、Measurements |
| [robotics](../assets/profiles/robotics.json) | 机电控制系统 | Motor、Mechanical、Power_Stage、Robotics、Simulation、Course |

按实际需求选择最小覆盖范围。编号是稳定分类，00_Project_Management 和 00_Reference 并存；
空缺编号有意保留，不表示某阶段尚未完成。目录只表示资料职责，不预置设计文件或供应商工具工程。
firmware 和 embedded-fullstack 不生成课程；只有 robotics 包含 10_Course。

Profile schema 与生成器 version 分开记录。换 Profile 或更改名称可能产生清单/README 冲突，
由用户审查后另行维护，不能通过覆盖完成隐式迁移。额外用户目录允许保留。
完整用法见 [README](../README.md)。
