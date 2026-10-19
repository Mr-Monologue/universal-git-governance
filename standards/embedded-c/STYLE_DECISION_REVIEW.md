# Embedded C 风格决策评审 — Draft 0.1.0

本轮是稳定化准备，不是规范冻结。所有推荐为 **PROPOSED**，所有个人决策保持 **OPEN**。
Doxygen 文件、公开 API、公开类型及相关接口契约为既定强制要求，不能被文本语言或排版选择降级。
[决策索引](OPEN_DECISIONS.md) / [实际 C/H 对照](examples/style-review/README.md)。

## 审阅依据和现状

原始输入为 Task 002 包 `Engineering_System_Task002_Bundle.zip` 的 `inputs/original-checklist.md`，
内容标题《MISRA C和C语言编程规范check list》，本次完整只读复核。
该条目的 SHA-256：`d8d6f4f5d5c296aa2b0135e01f98a0e33ccb9b8ff4f60180ff9e4cfbacaa7c13`。
下面的“原 Checklist”均指该原件的标题路径，不把后来的 REVIEW_CHECKLIST 冒充原件。
原件仅保留为仓库外历史输入，不复制其个人身份、特定硬件或许可证模板。

当前唯一规范正文为 [C_CODING_STANDARD.md](C_CODING_STANDARD.md)，状态 Draft 0.1.0。
现有配置是 LLVM 基础上的 Attach、4 空格、UseTab Never、100 列、右侧指针对齐；并非用户批准值。
ADC 示例已经按候选配置排版；正文 4.1 等历史片段仍采用函数左括号换行，本次不批量重排。
Skill 生成器仅产出无业务函数的 C/H 骨架，限制的是文件名 snake_case，不是对所有项目 API 的命名裁决。

## C-STYLE-01 — 大括号

状态：OPEN；推荐：PROPOSED。

- 当前行为：正文第 3 节建议 K&R，配置实际为 `BreakBeforeBraces: Attach`；ADC 函数和控制块均同行。
- 原 Checklist：“控制流与结构”“函数设计与模块化”示例多为同行大括号，但没有统一规范性选择。
- 推荐：新项目候选沿用 Attach，明确函数和控制块都同行；这里的 K&R 标签指该具体配置，不混淆传统 K&R 中函数另起一行的变体。
- 替代：Allman，函数及控制块左括号单独一行；也可由项目选择混合风格。
- 权衡及理由：Attach 更紧凑，Allman 便于垂直扫描。没有一方在 C 语义或安全性上天然更强；沿用候选可减少无意义格式差异。
- 将来影响：项目 clang-format、正文片段、未来函数模板、示例格式检查。无用户批准不得改写既有工程。

## C-STYLE-02 — 缩进与 Tab

状态：OPEN；推荐：PROPOSED。

- 当前行为：`IndentWidth: 4`、`UseTab: Never`；C/H 骨架使用空格。没有显式冻结 TabWidth。
- 原 Checklist：“C语言编程规范Check list / 缩进和代码风格”同时写“4个空格”和“使用tab”；文件头示例另写 1 tab == 4 spaces。视觉宽度与存储字符被混在一起。
- 推荐：缩进存储为 4 个空格；展示旧文件 Tab 时可用宽度 4，但不因此往新文件写入 Tab。
- 替代：存储 Tab、项目规定 TabWidth=4；或 Tab 负责层级、空格负责对齐。
- 权衡及理由：空格在 diff、网页和编辑器中显示更一致；Tab 可按个人偏好改变展示宽度。不能把这项偏好说成语言安全规则。
- 将来影响：UseTab、IndentWidth、TabWidth、编辑器配置、模板和格式 CI；未批准不统一转换历史文件。

## C-STYLE-03 — 行宽

状态：OPEN；推荐：PROPOSED。

- 当前行为：候选 ColumnLimit=100；正文允许文档、长 URL 等合理例外。
- 原 Checklist：“缩进和代码风格”要求不超过 80 列；“函数声明和定义”要求长参数换行。
- 推荐：100 列作为新项目候选；参数和 Doxygen 描述按语义换行，不为凑列宽删除契约。
- 替代：80 列适合并排审查/窄终端，120 列适合宽屏及长模块前缀。
- 权衡及理由：80 更容易拆开签名和注释，120 的并排阅读成本更大；100 是折中判断，不是技术标准规定。
- 将来影响：ColumnLimit、注释重排选项、生成模板及格式检查。中文字符的显示列宽不等于 UTF-8 字节数；对照用 ASCII 契约文字保证可重复计数，不能据此批准英文优先。

## C-STYLE-04 — 标识符命名

状态：OPEN；推荐：PROPOSED。

- 当前行为：公开 `adc_scale_convert_mv` 有模块前缀，变量 snake_case，枚举值 ADC_SCALE_*；无全局可变对象。生成器只接受小写 snake_case 文件名。
- 原 Checklist：“命名规范”要求全局 g_、局部小写下划线、指针 p_、函数指针 pf_、宏和枚举项大写；“宏定义和枚举”重复大写约定。
- 推荐：公开符号带模块前缀、函数/变量 snake_case、宏/枚举值 MODULE_UPPER_SNAKE_CASE；私有对象优先 static，不普遍要求类型前缀。
- 替代：项目统一 g_/p_/pf_，例如 `g_sample_count`、`p_result_mv`、`pf_sample_notify`，保留原偏好。
- 权衡及理由：模块前缀减少 C 全局符号碰撞；类型前缀便于快速识别，也可能随类型变化失真。前缀不能表达所有权、有效期或线程安全。
- 将来影响：公开 API/ABI、生成器允许的文件名、模板、静态分析命名规则及文档；不批量改名。

## C-STYLE-05 — 类型约定

状态：OPEN；推荐：PROPOSED。

- 当前行为：`adc_scale_status` typedef 无 _t；参数使用 uint16_t/uint32_t，乘法中间量 uint64_t；不假定枚举的 ABI 宽度。
- 原 Checklist：“基本语法与数据类型”要求固定长度类型；“命名规范”要求枚举变量 _T、typedef _t。变量后缀与类型后缀应分别决定。
- 推荐：公开类型采用 `module_status` 等语义名称；协议/硬件宽度在工具链提供时用精确宽度整数，长度用 size_t，状态不直接序列化为枚举内存布局。
- 替代：非 POSIX 的既有 MCU 项目可保留 module_status_t 和旧变量后缀；需要固定 ABI 时单独定义编码及转换。
- 权衡及理由：POSIX 名称空间保留 _t 后缀，不应误称为所有 ISO C 项目的全面禁用；跨平台公共接口避免新增 _t 更稳妥。固定宽度类型也不自动证明单位、范围和溢出安全。
- 将来影响：公开头文件、FFI、二进制协议、测试和调用者；既有 ABI 不因本建议而改动。

## C-STYLE-06 — C 语言版本

状态：OPEN；推荐：PROPOSED。

- 当前行为：宿主 GCC 测试显式使用 C11；正文允许受限项目 C99、C23 显式选择，未更改 MCU 工具链。
- 原 Checklist：“基本语法与数据类型”只要求标准 C，没有指定年代版本。
- 推荐：新项目先以显式 C11 做候选基线；保留 C99 项目。采用 C23 前对目标编译器、标准库、分析器及 ABI 做实际验证。
- 替代：C99 有较广的旧工具链覆盖；C23 提供新语法和库能力，适合已验证的现代链路。C17 也可作为 C11 勘误基线由项目选择。
- 权衡及理由：C11 的静态断言等有价值，但原子操作不保证无锁，线程库不保证在裸机可用；宿主 GCC 支持不代表 MCU 库支持。GCC 的默认标准会随版本改变，不能依赖默认值。[GCC 支持表](https://gcc.gnu.org/projects/c-status.html)
- 将来影响：构建 -std、工具链最低版本、SDK/库、模板关键字和 CI 矩阵；本轮不升级软件、不切换全局标准。

## C-STYLE-07 — Doxygen 注释语言

状态：OPEN；推荐：PROPOSED。

- 当前行为：规范及 ADC 契约中文，标识符和 Doxygen 标签英文；文件模板使用中文 brief。
- 原 Checklist：“注释与文档”要求注释清晰并符合项目风格，例子中英文混合，未正式选择文本语言。
- 推荐：按项目配置选择主语言；个人中文项目可延续中文候选，国际协作公共库优先评估英文。
- 替代：全局中文优先；全局英文优先；必要时维护双语摘要而非重复整份易漂移的契约。
- 权衡及理由：维护者理解和目标读者决定成本；语言选择不改变 @param 方向、单位、范围、返回状态、上下文等强制契约。[Doxygen 命令](https://www.doxygen.nl/manual/commands.html)
- 将来影响：模板文字、Doxygen OUTPUT_LANGUAGE/INPUT_ENCODING、文档审查；本轮对照英文只用于稳定列宽展示。

## C-STYLE-08 — 质量门禁

状态：OPEN；推荐：PROPOSED。

- 当前行为：宿主示例使用 C11、Wall/Wextra/Wpedantic/Wconversion/Wsign-conversion/Werror；CI 保留编译和 Python 检查。格式配置已存在，Doxygen 尚无统一目标项目配置。
- 原 Checklist：“防御性编程与安全性”要求静态分析；“缩进和代码风格”要求统一排版，没有给出 clang-format 版本或具体告警集。
- 推荐：项目冻结工具版本和用户维护代码范围，先编译告警及行为测试，再格式/Doxygen 和适用静态分析；新维护公开 API 的 Doxygen 强制地位不变。
- 替代：旧工程渐进基线、第三方 SDK 单独范围；严格工程在本项目代码开启 Werror 和更多检查，但不能为了通过而隐藏问题。
- 权衡及理由：Wall 不等于全部告警，告警存在编译器版本差异；格式通过不能证明契约或并发安全。Doxygen 的文档告警也不证明单位/ISR 承诺真实。[GCC 告警](https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html)、[Doxygen 配置](https://www.doxygen.nl/manual/config.html)
- 将来影响：项目 CI、编译选项、Doxyfile、clang-format 和分析器配置；具体工具选型与范围仍待批准。

## C-STYLE-09 — MISRA / 安全性层级

状态：OPEN；推荐：PROPOSED。

- 当前行为：规范不声明 MISRA 合规；general-embedded、hard-realtime、safety-critical、legacy-compatible 均是待项目选择的 Profile。
- 原 Checklist：标题包含 MISRA；“防御性编程与安全性”要求静态分析；文件头示例建议关键嵌入式系统遵循 MISRA，但没有版本、规则映射或偏离台账。
- 推荐：普通嵌入式先保证契约/边界/编译测试；严格工程追加分析、覆盖率目标和实时证据；安全关键工程另行确定适用标准版本、工具配置、偏离审批及独立审查。
- 替代：有合同要求的普通项目也可采用正式 MISRA 流程；不能只凭“非安全项目”免除既有组织要求。
- 权衡及理由：安全性证据是系统性工程投入，自制 Checklist、编译无警告和某个扫描器结果均不是认证。[MISRA Compliance:2020](https://www.misra.org.uk/app/uploads/2021/06/MISRA-Compliance-2020.pdf)
- 将来影响：风险分类、验证计划、分析器/许可证、偏离与证据归档；本任务不选定安全等级或声称合规。

## C-STYLE-10 — 条件比较方向（保留历史未决项）

状态：OPEN；推荐：PROPOSED。

- 当前行为：ADC 使用变量在左的比较；原 Checklist“条件判断”要求常数在 == 左侧。
- 推荐：语义自然的变量在左候选，配合编译器告警；替代为项目统一常量在左。
- 权衡及理由：常量在左可让某些误写赋值编译失败，但不能替代类型检查和测试；不应无关重写比较或短路顺序。
- 将来影响：示例、审查规则和静态分析配置；保留用户选择。

## C-STYLE-11 — 文件头元数据（保留历史未决项）

状态：OPEN；推荐：PROPOSED。

- 当前行为：模板只有真实文件名、brief 和职责，不自动生成作者、日期、许可证。原 Checklist“文件头注释检查”要求作者、版本、时间戳和历史表。
- 推荐：真实许可证按项目要求维护，Git 记录历史；替代为法规/交付要求下额外维护元数据。
- 权衡及理由：重复历史易过期，但正式交付要求优先；无论选择哪种都禁止虚构身份或许可证。
- 将来影响：文件头模板、交付检查和项目文档规则；本轮不添加自动元数据。

## 工程一致性与分发决定

本文件及代码对照只在 standards 人工维护。为满足 OPEN 索引的相对链接及离线可读性，
两份 Markdown 经已有同步脚本生成只读 references 副本；不分发编译输出、不引入第二人工源。
这是对“默认仅留 standards”的小幅调整，理由是避免破坏独立安装后的索引导航。
现有配置、模板排版和生成器 CLI 不变，Skill README 补充项目规则优先及 Draft 预设边界。

新增只读检查仅保护明确状态字段和契约标记，不能理解任意自然语言、证明所有函数契约完整或判定 MISRA 合规。
未来用户批准某项后，需要在独立授权变更中同时更新决策状态及验证预期，本轮不得自行标成已批准。
排版选项解释见 [ClangFormat 官方说明](https://clang.llvm.org/docs/ClangFormatStyleOptions.html)；
_t 保留边界见 [POSIX 名称空间 2.2.2](https://pubs.opengroup.org/onlinepubs/9799919799/functions/V2_chap02.html)。
