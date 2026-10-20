# Tests

用途：验证通用工具与仓库结构；预期内容是可重复运行的行为测试。
边界：不替代项目业务测试或人工规范审查，不宣称 Planned 组件已通过验证。
模块骨架状态：Scaffold / 尚未实现功能；基础仓库结构验证的单元测试已实现。

```bash
python -m unittest discover -s tests -v
```

被测工具：[validate_repository.py](../scripts/validate_repository.py)。
返回 [工程体系入口](../README.md)。
