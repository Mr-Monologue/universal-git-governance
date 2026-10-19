# C/H 风格对照 — Draft / PROPOSED

所有排版和命名方案均为 OPEN，示例不批准任何风格；Doxygen 强制要求不变。
[完整评审](../../STYLE_DECISION_REVIEW.md) / [决策索引](../../OPEN_DECISIONS.md)。

以下都是同一接口和算法：输出 min(sample_mv, ceiling_mv)，有效电压为 0–5000 mV。
checked API 拒绝 NULL 和越界并保持输出；assume_valid API 由调用方证明前置条件。
NULL 检查不能证明非 NULL 指针未悬空、已对齐或有足够空间。内部已证明的路径不必机械重复判空；
公开不可信边界应报告可检测的错误，不能把“性能优化”当作省略有效性证明的理由。
这些是宿主机审阅夹具，不是生产驱动；ISR 可调用性取决于目标时限与输出独占条件，未做 MCU 证明。

## 80 / 100 / 120 列头文件

每个块都可保存为 style_sample.h，与下方任一源文件组合编译。
由 clang-format 20.1.1 的 LLVM 基础、4 空格、UseTab Never、Attach、ReflowComments=true 生成，
只改变 ColumnLimit。保留 Doxygen 全文，签名/注释只改变换行。ASCII 文本便于复核列数，不代表批准英文策略。
若某标签的短句没有变化，是该宽度下无需重排，并非省略契约。

### 80 列

<!-- sample: header-80 -->
```c
/**
 * @file style_sample.h
 * @brief Style-review fixture, not a production hardware driver.
 */
#ifndef STYLE_SAMPLE_H_
#define STYLE_SAMPLE_H_
#include <stdint.h>
/** @brief Result of checked voltage limiting. */
typedef enum {
    SAMPLE_OK = 0,         /**< Success. */
    SAMPLE_INVALID_ARG = 1 /**< Null output or voltage outside range. */
} sample_status;
/**
 * @brief Limit a sampled voltage to a configured ceiling without allocating
 * memory or accessing hardware.
 * @param[in] sample_mv Sample voltage in mV, valid range [0, 5000].
 * @param[in] ceiling_mv Ceiling voltage in mV, valid range [0, 5000].
 * @param[out] result_mv Writable output in mV. NULL is rejected; output is
 * unchanged on error.
 * @retval SAMPLE_OK The output receives min(sample_mv, ceiling_mv).
 * @retval SAMPLE_INVALID_ARG NULL output or a voltage outside [0, 5000].
 * @note Non-NULL output must point to a live, aligned, writable uint16_t
 * object; caller retains ownership.
 * @note No shared state or blocking. ISR use requires target timing validation
 * and exclusive output access.
 */
sample_status sample_limit_checked(uint16_t sample_mv, uint16_t ceiling_mv,
                                   uint16_t *result_mv);
/**
 * @brief Limit a voltage on a path whose caller has already established the
 * contract.
 * @param[in] sample_mv Sample voltage in mV, range [0, 5000].
 * @param[in] ceiling_mv Ceiling voltage in mV, range [0, 5000].
 * @param[out] result_mv Receives min(sample_mv, ceiling_mv) in mV.
 * @pre result_mv points to a live, aligned, writable uint16_t object and is not
 * NULL.
 * @pre Both input voltages are in [0, 5000]; caller guarantees exclusive output
 * access.
 * @note No blocking or shared state. ISR use still requires target timing
 * validation.
 * @note No error status is returned; invalid calls violate the contract and may
 * cause undefined behavior.
 */
void sample_limit_assume_valid(uint16_t sample_mv, uint16_t ceiling_mv,
                               uint16_t *result_mv);
#endif
```

### 100 列

<!-- sample: header-100 -->
```c
/**
 * @file style_sample.h
 * @brief Style-review fixture, not a production hardware driver.
 */
#ifndef STYLE_SAMPLE_H_
#define STYLE_SAMPLE_H_
#include <stdint.h>
/** @brief Result of checked voltage limiting. */
typedef enum {
    SAMPLE_OK = 0,         /**< Success. */
    SAMPLE_INVALID_ARG = 1 /**< Null output or voltage outside range. */
} sample_status;
/**
 * @brief Limit a sampled voltage to a configured ceiling without allocating memory or accessing
 * hardware.
 * @param[in] sample_mv Sample voltage in mV, valid range [0, 5000].
 * @param[in] ceiling_mv Ceiling voltage in mV, valid range [0, 5000].
 * @param[out] result_mv Writable output in mV. NULL is rejected; output is unchanged on error.
 * @retval SAMPLE_OK The output receives min(sample_mv, ceiling_mv).
 * @retval SAMPLE_INVALID_ARG NULL output or a voltage outside [0, 5000].
 * @note Non-NULL output must point to a live, aligned, writable uint16_t object; caller retains
 * ownership.
 * @note No shared state or blocking. ISR use requires target timing validation and exclusive output
 * access.
 */
sample_status sample_limit_checked(uint16_t sample_mv, uint16_t ceiling_mv, uint16_t *result_mv);
/**
 * @brief Limit a voltage on a path whose caller has already established the contract.
 * @param[in] sample_mv Sample voltage in mV, range [0, 5000].
 * @param[in] ceiling_mv Ceiling voltage in mV, range [0, 5000].
 * @param[out] result_mv Receives min(sample_mv, ceiling_mv) in mV.
 * @pre result_mv points to a live, aligned, writable uint16_t object and is not NULL.
 * @pre Both input voltages are in [0, 5000]; caller guarantees exclusive output access.
 * @note No blocking or shared state. ISR use still requires target timing validation.
 * @note No error status is returned; invalid calls violate the contract and may cause undefined
 * behavior.
 */
void sample_limit_assume_valid(uint16_t sample_mv, uint16_t ceiling_mv, uint16_t *result_mv);
#endif
```

### 120 列

<!-- sample: header-120 -->
```c
/**
 * @file style_sample.h
 * @brief Style-review fixture, not a production hardware driver.
 */
#ifndef STYLE_SAMPLE_H_
#define STYLE_SAMPLE_H_
#include <stdint.h>
/** @brief Result of checked voltage limiting. */
typedef enum {
    SAMPLE_OK = 0,         /**< Success. */
    SAMPLE_INVALID_ARG = 1 /**< Null output or voltage outside range. */
} sample_status;
/**
 * @brief Limit a sampled voltage to a configured ceiling without allocating memory or accessing hardware.
 * @param[in] sample_mv Sample voltage in mV, valid range [0, 5000].
 * @param[in] ceiling_mv Ceiling voltage in mV, valid range [0, 5000].
 * @param[out] result_mv Writable output in mV. NULL is rejected; output is unchanged on error.
 * @retval SAMPLE_OK The output receives min(sample_mv, ceiling_mv).
 * @retval SAMPLE_INVALID_ARG NULL output or a voltage outside [0, 5000].
 * @note Non-NULL output must point to a live, aligned, writable uint16_t object; caller retains ownership.
 * @note No shared state or blocking. ISR use requires target timing validation and exclusive output access.
 */
sample_status sample_limit_checked(uint16_t sample_mv, uint16_t ceiling_mv, uint16_t *result_mv);
/**
 * @brief Limit a voltage on a path whose caller has already established the contract.
 * @param[in] sample_mv Sample voltage in mV, range [0, 5000].
 * @param[in] ceiling_mv Ceiling voltage in mV, range [0, 5000].
 * @param[out] result_mv Receives min(sample_mv, ceiling_mv) in mV.
 * @pre result_mv points to a live, aligned, writable uint16_t object and is not NULL.
 * @pre Both input voltages are in [0, 5000]; caller guarantees exclusive output access.
 * @note No blocking or shared state. ISR use still requires target timing validation.
 * @note No error status is returned; invalid calls violate the contract and may cause undefined behavior.
 */
void sample_limit_assume_valid(uint16_t sample_mv, uint16_t ceiling_mv, uint16_t *result_mv);
#endif
```

## K&R/Attach 与 Allman 实现

两个块均保存为 style_sample.c；函数和 if 控制块一起对比。仅空白改变，错误处理顺序和算法一致。

### Attach

<!-- sample: source-attach -->
```c
/**
 * @file style_sample.c
 * @brief Pure voltage limiting used only for formatting and contract review.
 */
#include "style_sample.h"
#include <stddef.h>
void sample_limit_assume_valid(uint16_t sample_mv, uint16_t ceiling_mv, uint16_t *result_mv) {
    *result_mv = (sample_mv > ceiling_mv) ? ceiling_mv : sample_mv;
}
sample_status sample_limit_checked(uint16_t sample_mv, uint16_t ceiling_mv, uint16_t *result_mv) {
    if ((result_mv == NULL) || (sample_mv > 5000U) || (ceiling_mv > 5000U)) {
        return SAMPLE_INVALID_ARG;
    }
    sample_limit_assume_valid(sample_mv, ceiling_mv, result_mv);
    return SAMPLE_OK;
}
```

### Allman

<!-- sample: source-allman -->
```c
/**
 * @file style_sample.c
 * @brief Pure voltage limiting used only for formatting and contract review.
 */
#include "style_sample.h"
#include <stddef.h>
void sample_limit_assume_valid(uint16_t sample_mv, uint16_t ceiling_mv, uint16_t *result_mv)
{
    *result_mv = (sample_mv > ceiling_mv) ? ceiling_mv : sample_mv;
}
sample_status sample_limit_checked(uint16_t sample_mv, uint16_t ceiling_mv, uint16_t *result_mv)
{
    if ((result_mv == NULL) || (sample_mv > 5000U) || (ceiling_mv > 5000U))
    {
        return SAMPLE_INVALID_ARG;
    }
    sample_limit_assume_valid(sample_mv, ceiling_mv, result_mv);
    return SAMPLE_OK;
}
```

## 两种命名方案（声明对照，不增加硬件行为）

A 使用模块前缀和语义名，B 演示原 Checklist 的 g_/p_/pf_ 与 _t/_T 候选。
以下片段不是额外的模板，不和上面的同名类型在一个翻译单元混用；不更改已有 ABI。
全局量演示的是显式文件作用域声明，实际设计仍应优先私有 static/实例状态。
函数指针的所有权、上下文和可空性仍须另写契约，前缀不能代替这些信息。

```c
/* A: module + semantic names */
typedef enum { SAMPLE_READY = 0, SAMPLE_ERROR = 1 } sample_state;
typedef void (*sample_notify)(uint16_t voltage_mv);
extern uint32_t sample_count;
sample_state sample_read(uint16_t *result_mv, sample_notify notify);
/* Local spellings: measured_mv, result_mv, notify, state. */
```

```c
/* B: historical prefixes and suffixes; not a POSIX-portable default */
typedef enum { SAMPLE_READY = 0, SAMPLE_ERROR = 1 } sample_state_t;
typedef void (*sample_notify_t)(uint16_t voltage_mv);
extern uint32_t g_sample_count;
sample_state_t sample_read(uint16_t *p_result_mv, sample_notify_t pf_notify);
/* Local spellings: measured_mv, p_result_mv, pf_notify, state_T. */
```

宏与枚举值在两种方案下均可使用 SAMPLE_*；_T 是原件对枚举变量的偏好，不能误当成 C 类型语法。
这些局部命名对比不声明 g_ 或 _t 已批准。公开真实类型仍需类似上方完整头文件中的 Doxygen 文档。

## 可重复验证

测试从带 sample 标记的 5 个 C 代码块提取内容，校验只改变排版、列宽上限和契约标签，
在仓库外用 C99/C11 编译 3 种头文件与 2 种实现组合，并执行边界、错误输出不变与有效路径等价断言。
编译器缺失时报告 NOT RUN。现有配置仅作用于原 ADC 示例，不用它把 Allman 对照重排成 Attach。
工具命令为 `python -m unittest discover -s tests -v`；生成器回归继续使用原安全 CLI。
