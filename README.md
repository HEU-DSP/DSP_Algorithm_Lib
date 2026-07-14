# DSP Algorithm Library

哈尔滨工程大学 DSP 爱好者协会 — 信号处理算法库。

纯算法代码，平台无关。仅依赖 `<stdint.h>`、`<math.h>` 和 ARM CMSIS-DSP。

## 目录结构

```
DSP_Algorithm_Lib/
├── backend/                          硬件抽象层（ADC）
│   ├── adc_backend.h                 接口定义
│   ├── adc_backend_stm32f407.c       STM32F407 后端（12-bit ADC）
│   ├── adc_backend_stm32h723.c       STM32H723 后端（16-bit ADC）
│   └── adc_backend_stm32h743.c       STM32H743 后端（16-bit ADC）
│
├── 测频/
│   ├── FFT实现/                      自定义基-2 FFT
│   └── FFT二次插值测频/              FFT 二次插值频率估计
│
├── 测幅/
│   ├── 均方根测幅/                   RMS 幅度测量
│   ├── 差分三角波测幅/               差分法三角波幅度测量
│   ├── 平顶窗FFT测幅/               平顶窗 FFT 幅度测量
│   └── CZT频谱细化/                 CZT Zoom-FFT 频谱细化
│
└── 测相/
    ├── 正交解调测相/                 I/Q 正交解调相位估计
    └── FIR滤波/                      FIR 带通滤波器
```

## 模块说明

### 测频

| 文件 | 函数 | 说明 |
|------|------|------|
| `FFTNt.c/.h` | `InitTableFFT(n)`, `cfft(ptr, n)` | 自定义基-2 FFT，不依赖 CMSIS-DSP FFT |
| `Fre.c/.h` | `cfft_f32_fre(fs, AD_Value, flag)` | 基于 FFT 的二次插值频率估计 |

### 测幅

| 文件 | 函数 | 说明 |
|------|------|------|
| `MAG.c/.h` | `Measuring_Sine_Amplitude(len, AD_value)` | 正弦波 RMS 幅度 |
| | `Measuring_Square_Amplitude(len, AD_value)` | 方波 RMS 幅度 |
| | `Measuring_Triangle_Amplitude(len, AD_value)` | 三角波 RMS 幅度 |
| `differAMP(1).c/.h` | `Differ_Tri_Amp(len, AD_value)` | 差分法三角波峰峰值 |
| `flat_top_data(1).c/.h` | `Sin_Amp_FFT(AD_Value)` | 平顶窗 FFT 正弦波幅度 |
| | `Square_Amp_FFT(AD_Value)` | 平顶窗 FFT 方波幅度 |
| | `Triangle_Amp_FFT(AD_Value)` | 平顶窗 FFT 三角波幅度 |
| `Zoom_FFT.c/.h` | `czt_Init_0(input, FS, f_start, f_end, zoom_abs)` | CZT 频谱细化初始化 |
| | `czt_result_fre(FS, f_start, f_end, zoom_abs)` | CZT 细化频率估计 |
| | `czt_Amp(FS, f_start, f_end, zoom_abs)` | CZT 细化幅度估计 |
| | `czt_Phase(FS, f_start, f_end, zoom_abs)` | CZT 细化相位估计 |

### 测相

| 文件 | 函数 | 说明 |
|------|------|------|
| `ffttest.c/.h` | `CalPhase(f, fs, N, adc_float)` | 正交解调相位估计 |
| | `CalXiebo(input, output, n)` | 谐波分析（FFT + 幅度谱） |
| | `Create_data2handle(p)` | 构造 FFT 复数输入 |
| `MAG_phase.c/.h` | `Measuring_Sine/Square/Triangle_Amplitude()` | 测相模块配套幅度测量 |
| `data.c/.h` | — | FFT 缓冲区与常量定义 |
| `IIR.c/.h` | `arm_emg_f32_filter_init()` | FIR 带通滤波器初始化 |
| | `arm_emg_f32_filter(input, output)` | FIR 带通滤波 |

### Backend

| 文件 | 函数 | 说明 |
|------|------|------|
| `adc_backend.h` | `ADC_Backend_RawToVoltage()` | ADC 原始数据转电压（接口） |
| `adc_backend_stm32f407.c` | | 12-bit ADC, VREF=3.3V |
| `adc_backend_stm32h723.c` | | 16-bit ADC, VREF=3.3V |
| `adc_backend_stm32h743.c` | | 16-bit ADC, VREF=3.3V |

## 依赖

- ARM CMSIS-DSP（`arm_math.h`、`arm_const_structs.h`、`arm_common_tables.h`）
- 标准库：`<stdint.h>`、`<math.h>`

## 使用方式

1. 将所需算法文件复制到你的工程
2. 确保工程已链接 CMSIS-DSP 库
3. 根据目标芯片选择一个 backend `.c` 文件链接：
   - STM32F407 → `adc_backend_stm32f407.c`
   - STM32H723 → `adc_backend_stm32h723.c`
   - STM32H743 → `adc_backend_stm32h743.c`
4. 在代码中 `#include "adc_backend.h"` 调用 ADC 接口

```c
#include "adc_backend.h"
#include "ffttest.h"

// 采集完成后
ADC_Backend_RawToVoltage(ADC_CHANNEL_1, float_buf, 1024);
float phase = CalPhase(50.0f, 51200.0f, 1024, float_buf);
```
