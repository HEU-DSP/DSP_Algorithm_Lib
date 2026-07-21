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
│   ├── FFT实现/                          自定义基-2 FFT
│   ├── FFT二次插值测频/              FFT 频谱峰值插值测频
│   └── 过零比较测频/              过零比较频率测量
│
├── 测幅/
│   ├── 均方根测幅/                          RMS 幅度测量
│   ├── 差分三角波测幅/                 差分法三角波幅度测量
│   ├── 平顶窗FFT测幅/                  平顶窗 FFT 幅度测量
│   └── CZT频谱细化/                          CZT Zoom-FFT 频谱细化
│
├── 测相/
│   ├── 正交解调测相/                     I/Q 正交解调相位估计
│   └── FIR滤波/                   FIR 带通滤波器
│
└── test/                             CMake + Python 仿真验证框架
```

## 目录迁移与兼容性（Breaking）

本次整理将旧中文目录和含义不清的文件名统一为中文领域目录。算法函数名大多保留，但旧的 `#include` 路径不再源码兼容，已有工程需要按下表更新头文件路径：

| 旧头文件 | 新头文件 |
|----------|----------|
| `FFTNt.h` | `测频/FFT实现/fft_n.h` |
| `Fre.h` | `测频/FFT二次插值测频/fft_interp_freq.h` |
| `zero_cross.h` | `测频/过零比较测频/zero_cross.h` |
| `MAG.h` | `测幅/均方根测幅/rms_amplitude.h` |
| `differAMP(1).h` | `测幅/差分三角波测幅/differ_amp.h` |
| `flat_top_data(1).h` | `测幅/平顶窗FFT测幅/flat_top_data.h` |
| `Zoom_FFT.h` | `测幅/CZT频谱细化/czt_zoom_fft.h` |
| `ffttest.h` | `测相/正交解调测相/iq_phase.h` |
| `data.h` | `测相/正交解调测相/fft_buffer.h` |
| `MAG_phase.h` | `测相/正交解调测相/mag_phase.h` |
| `IIR.h` | `测相/FIR滤波/fir_filter.h` |

这属于明确的 breaking include-path 迁移；合入后应同步修改下游工程的包含目录和 `#include` 语句。

## 模块说明

### 测频

| 文件 | 函数 | 说明 |
|------|------|------|
| `fft_n.c/.h` | `InitTableFFT(n)`, `cfft(ptr, n)` | 自定义基-2 FFT，不依赖 CMSIS-DSP FFT |
| `fft_interp_freq.c/.h` | `cfft_f32_fre(fs, AD_Value, flag)` | 基于 FFT 的对数抛物线插值频率估计 |
| `zero_cross.c/.h` | `ZeroCross_Freq(input, n, fs)` | 过零比较频率测量（线性插值） |
| | `ZeroCross_Period(input, n, fs)` | 过零比较周期测量 |
| | `ZeroCross_Count(input, n)` | 过零点计数 |

### 测幅

| 文件 | 函数 | 说明 |
|------|------|------|
| `rms_amplitude.c/.h` | `Measuring_Sine_Amplitude(len, AD_value)` | 正弦波 RMS 幅度 |
| | `Measuring_Square_Amplitude(len, AD_value)` | 方波 RMS 幅度 |
| | `Measuring_Triangle_Amplitude(len, AD_value)` | 三角波 RMS 幅度 |
| `differ_amp.c/.h` | `Differ_Tri_Amp(len, AD_value)` | 差分法三角波峰峰值 |
| `flat_top_data.c/.h` | `Sin_Amp_FFT(AD_Value)` | 平顶窗 FFT 正弦波幅度 |
| | `Square_Amp_FFT(AD_Value)` | 平顶窗 FFT 方波幅度 |
| | `Triangle_Amp_FFT(AD_Value)` | 平顶窗 FFT 三角波幅度 |
| `czt_zoom_fft.c/.h` | `czt_Init_0(input, FS, f_start, f_end, zoom_abs)` | CZT 频谱细化初始化 |
| | `czt_result_fre(FS, f_start, f_end, zoom_abs)` | CZT 细化频率估计 |
| | `czt_Amp(FS, f_start, f_end, zoom_abs)` | CZT 细化幅度估计 |
| | `czt_Phase(FS, f_start, f_end, zoom_abs)` | CZT 细化相位估计 |

### 测相

| 文件 | 函数 | 说明 |
|------|------|------|
| `iq_phase.c/.h` | `CalPhase(f, fs, N, adc_float)` | 带直流项的正弦最小二乘相位估计（无需相干采样） |
| | `CalXiebo(input, output, n)` | 谐波分析（FFT + 幅度谱） |
| | `Create_data2handle(p)` | 构造 FFT 复数输入 |
| `mag_phase.c/.h` | `Measuring_Sine/Square/Triangle_Amplitude()` | 测相模块配套幅度测量 |
| `fft_buffer.c/.h` | — | FFT 缓冲区与常量定义 |
| `fir_filter.c/.h` | `arm_emg_f32_filter_init()` | FIR 带通滤波器初始化 |
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

## 本地构建与验证

仓库根目录的 CMake 工程用于 PC 端仿真验证，不替代单片机工程自身的构建配置。首次拉取后先初始化 CMSIS-DSP 子模块：

```powershell
git submodule update --init --recursive
cmake -S . -B build -G "MinGW Makefiles" -DCMAKE_C_COMPILER=gcc
cmake --build build --target test_sanity
python test/python/run_test.py --module all --suite full
```

完整数据集验证和报告生成方式见 [`test/README.md`](test/README.md)。Python/NumPy 生成确定性的数学真值数组，CMake/GCC 编译并运行真实 C 源码。运行时数值验证覆盖自定义 FFT 核心的直接频率/幅值、FFT 插值与过零测频、RMS 测幅、I/Q 整周期与非相干频率的多角度/噪声测相、谐波分析、测相配套正弦/方波/三角波幅度及保护/非法输入、CZT 测频/测幅，以及 FIR 的确定性正弦和冲激 NumPy 卷积比较与零输入安全回归。差分三角波测幅、平顶窗 FFT 测幅、Backend 硬件转换和 `czt_Phase()` 未在这里数值建立；原始 FIR 设计缺少采样率规格，不能据此主张截止频率或通带性能。

完整验证与报告命令：

```powershell
python test/python/run_test.py --module frequency --suite full
python test/python/run_test.py --module phase --suite full
python test/python/run_test.py --module mag_phase --suite full
python test/python/run_test.py --module fir --suite full
python test/python/run_test.py --module all --suite full --save-json test/python/full_results.json
python test/python/report.py --input test/python/full_results.json --output test/validation_report.md --title "DSP 算法验证报告"
```

完整运行生成 16 条算法资源记录。BENCH 加 GNU `size -B` 输出仅为 PC/GCC 主机参考时间与可执行文件、`.text`、`.data`、`.bss` 节区大小；同一测试目标内的算法共享目标映像大小，并非单独函数大小。`test_sanity` 只用于配置、编译和链接环境检查，不是算法运行时资源目标。主机耗时会随机器与负载变化，不能复制为 STM32 性能或资源测量。

## 仓库组织说明

本项目是纯 C 算法库，继续按 `测频`、`测幅`、`测相` 和 `backend` 进行领域分层。每个算法目录直接保存配套 `.c/.h`，公共仿真与回归测试集中在 `test/`；不引入与本项目无关的 `bsp/drivers/services/app/ui` 嵌入式应用层目录。

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
#include "iq_phase.h"

// 采集完成后
ADC_Backend_RawToVoltage(ADC_CHANNEL_1, float_buf, 1024);
float phase = CalPhase(50.0f, 51200.0f, 1024, float_buf);
```
