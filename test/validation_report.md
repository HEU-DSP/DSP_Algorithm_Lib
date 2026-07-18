# DSP 算法验证报告

**Generated:** 2026-07-18 12:57:40

## Run metadata

| Field | Value |
|-------|-------|
| Suite | full |
| Seed | 20260717 |
| Generated Utc | 2026-07-18T04:57:29.214666+00:00 |
| Cmake | cmake version 4.4.0 |

## 修订结论

- 原报告中 RMS 三项约 1.54% 的统一偏高是实质缺陷：循环多处理了一个样本，但仍按原长度归一化。现已修正边界。
- 原报告中 CZT 幅值约为 1.5708 倍也是实质缺陷：归一化公式误乘了 π/2，并且峰值搜索越界。两项均已修正。
- 原报告的 45° 测相 PASS 属于假阳性。旧公式实际返回 `90° - 输入相位`，只有 45° 恰好相等；修订数据集覆盖负角、0°、90°、跨 ±180° 和噪声。
- 原报告只用整数 FFT 频点，未真正检验插值。修订后增加非整数频点，并采用对数抛物线插值。
- 表中 Expected 来自信号生成参数，不由另一份同类测量算法计算，避免 C 与 Python 同错。
- PASS 只代表本报告列出的确定性仿真用例；不等同于已完成硬件、全动态范围或所有信噪比验证。
- `czt_Phase()` 暂未列为已验证结果：当前实现没有保留去啁啾后的最终复数 CZT 输出。

## Summary

| Metric | Value |
|--------|-------|
| Total tests | 41 |
| PASS | 41 |
| FAIL | 0 |
| NO_RESULT | 0 |
| ERROR | 0 |
| Pass rate | 100.0% |

## 测频 (frequency)

| Case | Algorithm | Expected | Measured | Abs Error | Rel Error | Tolerance | Status |
|------|-----------|----------|----------|-----------|-----------|-----------|--------|
| integer_bin | fft_interp | 1000.000000 | 1000.000000 | +0.000000 | +0.0000% | relative error <= 0.1% | PASS |
| integer_bin | fft_peak | 1000.000000 | 1000.000000 | +0.000000 | +0.0000% | absolute error <= half FFT bin | PASS |
| integer_bin | zero_cross_freq | 1000.000000 | 999.999695 | +0.000305 | +0.0000% | relative error <= 0.1% | PASS |
| integer_bin | zero_cross_period | 0.001000 | 0.001000 | +0.000000 | +0.0000% | relative error <= 0.1% | PASS |
| non_integer_bin | fft_interp | 1003.700000 | 1004.558350 | +0.858350 | +0.0855% | relative error <= 0.1% | PASS |
| non_integer_bin | fft_peak | 1003.700000 | 1006.250000 | +2.550000 | +0.2541% | absolute error <= half FFT bin | PASS |
| non_integer_bin | zero_cross_freq | 1003.700000 | 1003.699768 | +0.000232 | +0.0000% | relative error <= 0.1% | PASS |
| non_integer_bin | zero_cross_period | 0.000996 | 0.000996 | +0.000000 | +0.0315% | relative error <= 0.1% | PASS |
| with_noise | fft_interp | 997.300000 | 998.025208 | +0.725208 | +0.0727% | relative error <= 0.1% | PASS |
| with_noise | fft_peak | 997.300000 | 1000.000000 | +2.700000 | +0.2707% | absolute error <= half FFT bin | PASS |
| with_noise | zero_cross_freq | 997.300000 | 997.268433 | +0.031567 | +0.0032% | relative error <= 0.1% | PASS |
| with_noise | zero_cross_period | 0.001003 | 0.001003 | +0.000000 | +0.0292% | relative error <= 0.1% | PASS |
| quantized_non_integer | fft_interp | 1234.500000 | 1234.776733 | +0.276733 | +0.0224% | relative error <= 0.1% | PASS |
| quantized_non_integer | fft_peak | 1234.500000 | 1237.500000 | +3.000000 | +0.2430% | absolute error <= half FFT bin | PASS |
| quantized_non_integer | zero_cross_freq | 1234.500000 | 1234.500366 | +0.000366 | +0.0000% | relative error <= 0.1% | PASS |
| quantized_non_integer | zero_cross_period | 0.000810 | 0.000810 | +0.000000 | +0.0055% | relative error <= 0.1% | PASS |

## 测幅 (amplitude)

| Case | Algorithm | Expected | Measured | Abs Error | Rel Error | Tolerance | Status |
|------|-----------|----------|----------|-----------|-----------|-----------|--------|
| sine_1v | rms_sine | 1.000000 | 0.999706 | +0.000294 | +0.0294% | relative error <= 0.5% | PASS |
| square_0p8v | rms_square | 0.800000 | 0.799524 | +0.000476 | +0.0595% | relative error <= 0.5% | PASS |
| triangle_1p2v | rms_triangle | 1.200000 | 1.200821 | +0.000821 | +0.0684% | relative error <= 0.5% | PASS |

## 测相 (phase)

| Case | Algorithm | Expected | Measured | Abs Error | Rel Error | Tolerance | Status |
|------|-----------|----------|----------|-----------|-----------|-----------|--------|
| phase_-170deg | iq_phase | -2.967060 | -2.967060 | +0.000000 | N/A | circular error <= 0.5 degree | PASS |
| phase_-170deg | xiebo_fundamental | 512.000000 | 511.999969 | +0.000031 | +0.0000% | relative error <= 0.5% | PASS |
| phase_-90deg | iq_phase | -1.570796 | -1.570796 | +0.000000 | N/A | circular error <= 0.5 degree | PASS |
| phase_-90deg | xiebo_fundamental | 512.000000 | 512.000000 | +0.000000 | +0.0000% | relative error <= 0.5% | PASS |
| phase_-30deg | iq_phase | -0.523599 | -0.523599 | +0.000000 | N/A | circular error <= 0.5 degree | PASS |
| phase_-30deg | xiebo_fundamental | 512.000000 | 512.000000 | +0.000000 | +0.0000% | relative error <= 0.5% | PASS |
| phase_+0deg | iq_phase | 0.000000 | -0.000000 | +0.000000 | N/A | circular error <= 0.5 degree | PASS |
| phase_+0deg | xiebo_fundamental | 512.000000 | 512.000000 | +0.000000 | +0.0000% | relative error <= 0.5% | PASS |
| phase_+45deg | iq_phase | 0.785398 | 0.785398 | +0.000000 | N/A | circular error <= 0.5 degree | PASS |
| phase_+45deg | xiebo_fundamental | 512.000000 | 512.000000 | +0.000000 | +0.0000% | relative error <= 0.5% | PASS |
| phase_+90deg | iq_phase | 1.570796 | 1.570796 | +0.000000 | N/A | circular error <= 0.5 degree | PASS |
| phase_+90deg | xiebo_fundamental | 512.000000 | 512.000000 | +0.000000 | +0.0000% | relative error <= 0.5% | PASS |
| phase_+170deg | iq_phase | 2.967060 | 2.967060 | +0.000000 | N/A | circular error <= 0.5 degree | PASS |
| phase_+170deg | xiebo_fundamental | 512.000000 | 511.999969 | +0.000031 | +0.0000% | relative error <= 0.5% | PASS |
| phase_45deg_noise | iq_phase | 0.785398 | 0.785369 | +0.000029 | N/A | circular error <= 0.5 degree | PASS |
| phase_45deg_noise | xiebo_fundamental | 512.000000 | 512.042908 | +0.042908 | +0.0084% | relative error <= 0.5% | PASS |

## CZT 频谱细化 (czt)

| Case | Algorithm | Expected | Measured | Abs Error | Rel Error | Tolerance | Status |
|------|-----------|----------|----------|-----------|-----------|-----------|--------|
| freq_1000p3_amp_0p7 | czt_freq | 1000.300000 | 1000.244263 | +0.055737 | +0.0056% | absolute error <= one CZT scan step | PASS |
| freq_1000p3_amp_0p7 | czt_amp | 0.700000 | 0.699798 | +0.000202 | +0.0289% | relative error <= 0.5% | PASS |
| freq_1234p6_amp_1p2 | czt_freq | 1234.600000 | 1234.635010 | +0.035010 | +0.0028% | absolute error <= one CZT scan step | PASS |
| freq_1234p6_amp_1p2 | czt_amp | 1.200000 | 1.199687 | +0.000313 | +0.0261% | relative error <= 0.5% | PASS |

## safety (safety)

| Case | Algorithm | Expected | Measured | Abs Error | Rel Error | Tolerance | Status |
|------|-----------|----------|----------|-----------|-----------|-----------|--------|
| fixed_size_wrappers | iq_invalid_length_unchanged | 1.000000 | 1.000000 | +0.000000 | +0.0000% | invalid length leaves output unchanged | PASS |
| fixed_size_wrappers | fir_zero_max_abs | 0.000000 | 0.000000 | +0.000000 | +0.0000% | zero-input FIR output <= 1e-6 | PASS |
