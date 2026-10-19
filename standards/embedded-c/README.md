# Embedded C Coding Standard — Draft v0.1.0

本包来自用户原始 C/MISRA Checklist 的现代化整理，不替代项目既有正式规范，也不授予 Agent Git 写入权限。

## 文件

- [C_CODING_STANDARD.md](C_CODING_STANDARD.md)：唯一完整规则正文，版本 0.1.0 / Draft。
- [REVIEW_CHECKLIST.md](REVIEW_CHECKLIST.md)：用于 Code Review/Agent 自检的任务验收清单。
- [CHANGE_REVIEW.md](CHANGE_REVIEW.md)：保留原 Checklist 语义，说明规则调整依据与集成修复。
- [OPEN_DECISIONS.md](OPEN_DECISIONS.md)：尚未冻结的个人风格和原 Checklist 差异。
- [STYLE_DECISION_REVIEW.md](STYLE_DECISION_REVIEW.md)：11 项 OPEN / PROPOSED 决策及技术权衡。
- [C/H 风格对照](examples/style-review/README.md)：同一契约的括号、列宽、命名及前置条件演示。
- [config/.clang-format](config/.clang-format)：建议格式设置，已用 clang-format 20.1.1 验证本目录示例，非全仓库强制。
- `examples/adc_scale.{h,c}` 和 `examples/test_adc_scale.c`：带 Doxygen API 的宿主机示例和边界测试。

## 参考测试

```bash
build_dir=$(mktemp -d)
cc -std=c11 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Werror \
  -I examples examples/adc_scale.c examples/test_adc_scale.c -o "$build_dir/adc_scale_test"
"$build_dir/adc_scale_test"
```

运行示例时将可执行文件输出到仓库外临时目录。该示例不证明 MCU 实时性或 MISRA 合规。

Doxygen 是已确定的强制要求；其他风格仍为 Draft 建议，既有项目/组织正式规范优先。
范围仅为规范、清单和可验证的示例，不提供正式 Embedded C Skill，也不授予 Git 操作权限。
[轻量验证脚本](../../scripts/validate_embedded_c.py) 只检查结构、文档和 Doxygen 注释存在性，
不能验证全部 Doxygen 语义、API 安全性或 MISRA 合规。

返回 [Standards](../README.md) / [Engineering System](../../README.md)。
