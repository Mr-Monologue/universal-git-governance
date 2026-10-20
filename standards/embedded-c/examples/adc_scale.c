/**
 * @file adc_scale.c
 * @brief ADC 换算实现。
 * @note 模块不访问硬件寄存器，不分配动态内存。
 */

#include "adc_scale.h"

#include <stddef.h>
#include <stdint.h>

adc_scale_status adc_scale_convert_mv(uint16_t raw_code, uint16_t full_scale_code,
                                      uint32_t reference_mv, uint32_t *result_mv) {
    if ((result_mv == NULL) || (full_scale_code == 0U) || (reference_mv == 0U) ||
        (raw_code > full_scale_code)) {
        return ADC_SCALE_INVALID_ARG;
    }

    /* 乘法及舍入均使用 uint64_t，避免 32 位溢出。 */
    const uint64_t numerator = (uint64_t)raw_code * (uint64_t)reference_mv;
    const uint64_t rounded =
        (numerator + ((uint64_t)full_scale_code / 2U)) / (uint64_t)full_scale_code;

    /* raw_code <= full_scale_code，故 rounded <= reference_mv。 */
    *result_mv = (uint32_t)rounded;
    return ADC_SCALE_OK;
}
