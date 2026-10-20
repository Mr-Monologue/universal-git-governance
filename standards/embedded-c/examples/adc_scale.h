/**
 * @file adc_scale.h
 * @brief ADC 原始采样码值换算为毫伏的可移植模块。
 *
 * 本接口仅进行数值换算，不负责硬件采样、校准和滤波。
 */

#ifndef ADC_SCALE_H_
#define ADC_SCALE_H_

#include <stdint.h>

/** @brief ADC 换算结果状态。 */
typedef enum {
    ADC_SCALE_OK = 0,          /**< 换算成功。 */
    ADC_SCALE_INVALID_ARG = 1, /**< 参数范围非法或输出指针为空。 */
} adc_scale_status;

/**
 * @brief 将 ADC 原始码值换算为电压（mV）。
 *
 * 符号：r = raw_code（无量纲计数），F = full_scale_code（无量纲满量程码），
 * V = reference_mv（mV），y = result_mv（mV）；0 <= r <= F，F > 0，V > 0。
 * 关系：y = floor((r * V + floor(F / 2)) / F)，即最接近的整数毫伏，半值向上舍入。
 *
 * @param[in] raw_code ADC 原始码值，范围为 [0, full_scale_code]。
 * @param[in] full_scale_code ADC 满量程码值，例如 12 位无符号码值为 4095；必须 > 0。
 * @param[in] reference_mv 参考电压，单位 mV，必须 > 0。
 * @param[out] result_mv 输出电压，单位 mV；非 NULL，仅成功时写入。
 * @retval ADC_SCALE_OK 参数有效，换算成功。
 * @retval ADC_SCALE_INVALID_ARG 参数非法，输出保持不变。
 * @note 这是理想比例换算，不含 ADC 误差或参考电压校准。
 * @note 使用 64 位中间结果避免乘法溢出；适合宿主机单元测试。
 * @note 本函数无静态可变状态；多个调用者不得同时写同一输出地址。
 */
adc_scale_status adc_scale_convert_mv(uint16_t raw_code, uint16_t full_scale_code,
                                      uint32_t reference_mv, uint32_t *result_mv);

#endif /* ADC_SCALE_H_ */
