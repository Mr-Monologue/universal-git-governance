/**
 * @file test_adc_scale.c
 * @brief ADC 换算模块的宿主机边界测试。
 */

#include "adc_scale.h"

#include <assert.h>
#include <stdint.h>
#include <stddef.h>

/**
 * @brief 执行 ADC 正常、错误输入和舍入边界断言。
 * @retval 0 所有断言通过；失败时由 assert 终止程序。
 */
int main(void) {
    uint32_t mv = 123U;

    assert(adc_scale_convert_mv(0U, 4095U, 3300U, &mv) == ADC_SCALE_OK);
    assert(mv == 0U);
    assert(adc_scale_convert_mv(4095U, 4095U, 3300U, &mv) == ADC_SCALE_OK);
    assert(mv == 3300U);
    assert(adc_scale_convert_mv(2048U, 4095U, 3300U, &mv) == ADC_SCALE_OK);
    assert(mv == 1650U);

    mv = 999U;
    assert(adc_scale_convert_mv(1U, 0U, 3300U, &mv) == ADC_SCALE_INVALID_ARG);
    assert(mv == 999U);
    assert(adc_scale_convert_mv(1U, 4095U, 0U, &mv) == ADC_SCALE_INVALID_ARG);
    assert(mv == 999U);
    assert(adc_scale_convert_mv(1U, 4095U, 3300U, NULL) == ADC_SCALE_INVALID_ARG);
    assert(adc_scale_convert_mv(4096U, 4095U, 3300U, &mv) == ADC_SCALE_INVALID_ARG);
    assert(mv == 999U);
    assert(adc_scale_convert_mv(65535U, 65535U, UINT32_MAX, &mv) == ADC_SCALE_OK);
    assert(mv == UINT32_MAX);
    assert(adc_scale_convert_mv(1U, 2U, 1U, &mv) == ADC_SCALE_OK);
    assert(mv == 1U);
    assert(adc_scale_convert_mv(1U, 3U, 1U, &mv) == ADC_SCALE_OK);
    assert(mv == 0U);
    return 0;
}
