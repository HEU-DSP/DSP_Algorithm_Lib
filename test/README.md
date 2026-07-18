# DSP 算法库仿真与验证指南

本目录用 Python/NumPy 生成确定性的数学真值数组，用 CMake/GCC 编译并运行真实 C 源码，再将输出与测试参数中注入的真值比较。验证程序不会用另一份同类算法计算“答案”，因此可以发现测相公式方向、幅值归一化等系统性错误。

## 一次性环境准备

需要：

- CMake 3.16 或更新版本；
- 支持 C99 的 GCC（Windows 推荐 MSYS2 UCRT64）；
- Python 3.9 或更新版本；
- NumPy；
- Git 子模块 `external/CMSIS-DSP`。

在仓库根目录执行：

```powershell
git submodule update --init --recursive
python -m pip install numpy
cmake -S . -B build -G Ninja -DCMAKE_C_COMPILER=gcc
```

如果 `cmake` 没加入 PATH，但 VS Code 的 CMake Tools 已经能完成 Configure，也可以先在 VS Code 中配置一次。测试脚本会从 `build/CMakeCache.txt` 自动找到 CMake。也可以显式传入：

```powershell
python test/python/run_test.py --cmake "C:\Program Files\CMake\bin\cmake.exe"
```

## 运行测试

快速冒烟测试：

```powershell
python test/python/run_test.py --module all --suite smoke
```

提交 PR 前运行完整数据集并生成报告：

```powershell
python test/python/run_test.py --module frequency --suite full
python test/python/run_test.py --module phase --suite full
python test/python/run_test.py --module mag_phase --suite full
python test/python/run_test.py --module fir --suite full
python test/python/run_test.py --module all --suite full --save-json test/python/full_results.json
python test/python/report.py --input test/python/full_results.json --output test/validation_report.md --title "DSP 算法验证报告"
```

只测一个模块：

```powershell
python test/python/run_test.py --module frequency --suite full
python test/python/run_test.py --module amplitude --suite full
python test/python/run_test.py --module phase --suite full
python test/python/run_test.py --module czt --suite full
python test/python/run_test.py --module fft_core --suite full
python test/python/run_test.py --module mag_phase --suite full
python test/python/run_test.py --module fir --suite full
python test/python/run_test.py --module safety --suite full
```

自定义单个用例必须使用 `--suite custom`：

```powershell
python test/python/run_test.py --module phase --suite custom --freq 50 --phase 0 --samples 1024
```

固定长度约束：FFT 测频为 8192 点、IQ 测相为 1024 点、CZT 为 2048 点。传入其他长度时，C runner 会在编译阶段明确失败，避免越界运行。

## 完整数据集覆盖范围

- 测频：整数频点、非整数频点、加噪、12 位量化；
- 自定义 FFT 核心：直接 FFT 频率和幅值；
- 测幅：正弦波、方波、三角波；
- 测相：`-170°、-90°、-30°、0°、45°、90°、170°` 和带噪 45°；
- CZT：两组非整数频率和不同幅值。
- 测相配套测幅：正弦、方波、三角波幅度，以及保护和非法输入检查；
- FIR：对给定 11 个归一化系数的 NumPy 卷积输出比较，并覆盖零输入安全；
- 安全回归：FIR 零输入、I/Q 谐波分析固定长度保护。

差分三角波测幅、平顶窗 FFT 测幅、Backend 硬件转换和 `czt_Phase()` 不在本次数值验证范围内，不能据此声称其数值正确。FIR 卷积仅按提供的 11 个归一化系数验证；原始滤波器设计未给出采样率规格，因此这里不主张截止频率或通带性能。

所有加噪用例默认使用随机种子 `20260717`，可用 `--seed` 修改并在 JSON 元数据中记录。

## 判定门限

| 项目 | 门限 |
|------|------|
| FFT 对数抛物线插值测频 | 相对误差不超过 0.1% |
| FFT 峰值频点 | 绝对误差不超过半个 FFT 频点 |
| 过零测频/周期 | 相对误差不超过 0.1% |
| RMS 测幅 | 相对误差不超过 0.5% |
| IQ 测相 | 圆周误差不超过 0.5° |
| CZT 测频 | 绝对误差不超过一个扫描步长 |
| CZT 测幅 | 相对误差不超过 0.5% |
| I/Q 非法长度 | 拒绝调用且不修改输出缓冲区 |
| FIR 零输入 | 1024 点输出最大绝对值不超过 `1e-6` |

CZT 的 `czt_Phase()` 当前只保留接口，没有纳入“已验证”结论，因为现有实现没有保存去啁啾后的复数输出，直接读取卷积缓冲区不能代表最终 CZT 相位。

## PC/GCC 资源参考

完整运行会在 JSON 的 `resources` 中保存 BENCH 平均耗时及 GNU `size -B` 的可执行文件、`.text`、`.data`、`.bss` 大小。它们都是 PC/GCC 主机参考值：主机时间会随机器和负载变化，不能复制为 STM32 性能；同一测试目标中的算法共享同一个目标映像大小，因此同目标的大小行不是单个函数的独立大小。

## 结果协议

C runner 每行输出：

```text
RESULT:<label>:<floating-point-value>
```

脚本将每个检查记录为 `PASS`、`FAIL`、`NO_RESULT` 或 `ERROR`。任何非 PASS 状态都会让进程返回非零退出码，因此模块编译或运行异常不会再从汇总中消失。
