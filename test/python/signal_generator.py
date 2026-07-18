"""测试信号生成模块。

支持正弦波、方波、三角波，可选加性高斯噪声和 ADC 量化模拟。
既可作为 Python 模块 import 使用，也支持命令行独立调用。
"""

import numpy as np
import os
import argparse
import sys


def generate_sine(freq, amplitude, phase, sample_rate, samples):
    """生成正弦波信号。"""
    t = np.arange(samples, dtype=np.float64) / sample_rate
    return (amplitude * np.sin(2 * np.pi * freq * t + phase)).astype(np.float32)


def generate_square(freq, amplitude, phase, sample_rate, samples):
    """生成方波信号。"""
    t = np.arange(samples, dtype=np.float64) / sample_rate
    raw = amplitude * np.sign(np.sin(2 * np.pi * freq * t + phase))
    return raw.astype(np.float32)


def generate_triangle(freq, amplitude, phase, sample_rate, samples):
    """生成三角波信号。"""
    t = np.arange(samples, dtype=np.float64) / sample_rate
    raw = 2 * np.abs(2 * ((freq * t + phase / (2 * np.pi)) % 1.0) - 1) - 1
    return (amplitude * raw).astype(np.float32)


def apply_adc_quantization(signal, adc_bits, vref):
    """模拟 ADC 量化：float 电压 → uint16 原始值 → 量化回 float。

    模拟实际 ADC 电路行为：信号叠加 VREF/2 直流偏置后采样，
    输出时去除直流偏置，还原为纯交流信号。
    """
    adc_max = (1 << adc_bits) - 1
    vref_half = vref / 2.0

    # 叠加直流偏置到 ADC 输入范围中心
    biased = signal + vref_half

    # 量化
    adc_raw = np.round(np.clip(biased / vref, 0, 1) * adc_max)
    adc_raw = np.clip(adc_raw, 0, adc_max).astype(np.uint16)

    # 还原为电压并去除直流偏置
    quantized = (adc_raw.astype(np.float32) / adc_max) * vref
    quantized = quantized - vref_half
    return quantized, adc_raw


def generate_signal(waveform, freq, amplitude, phase, sample_rate,
                    samples, noise_std=0.0, adc_bits=0, vref=3.3, seed=None):
    """生成测试信号。

    Args:
        waveform: "sine" | "square" | "triangle"
        freq: 信号频率 (Hz)
        amplitude: 信号幅度 (V)
        phase: 初始相位 (rad)
        sample_rate: 采样率 (Hz)
        samples: 采样点数
        noise_std: 高斯噪声标准差，0 表示不加噪声
        adc_bits: 0 表示不量化；12 或 16 表示模拟对应位宽的 ADC
        vref: ADC 参考电压，默认 3.3V

    Returns:
        (signal_float, adc_raw): signal_float 是 float32 数组，
        adc_raw 在 adc_bits==0 时为 None
    """
    generators = {
        'sine': generate_sine,
        'square': generate_square,
        'triangle': generate_triangle,
    }
    if waveform not in generators:
        raise ValueError(f"不支持的波形类型: {waveform}，可选 {list(generators.keys())}")

    signal = generators[waveform](freq, amplitude, phase, sample_rate, samples)

    # 加噪声
    if noise_std > 0:
        rng = np.random.default_rng(seed)
        noise = rng.normal(0, noise_std, samples).astype(np.float32)
        signal = signal + noise

    # ADC 量化
    adc_raw = None
    if adc_bits > 0:
        signal, adc_raw = apply_adc_quantization(signal, adc_bits, vref)

    return signal, adc_raw


def write_signal_header(signal_float, adc_raw, output_dir, metadata):
    """将信号数据写入 C 头文件。

    Args:
        signal_float: float32 信号数组
        adc_raw: uint16 ADC 原始值数组（可为 None）
        output_dir: 输出目录（通常是 test/generated/）
        metadata: dict，包含 waveform, freq, amplitude, phase, sample_rate, samples

    Returns:
        写入的文件路径
    """
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, 'signal_data.h')
    samples = len(signal_float)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('/* auto-generated test signal - do not edit manually */\n')
        f.write('#ifndef SIGNAL_DATA_H\n')
        f.write('#define SIGNAL_DATA_H\n\n')
        f.write('#include <stdint.h>\n')
        f.write('#include "arm_math.h"\n\n')

        # meta info macros
        f.write(f'#define SIGNAL_LENGTH    {samples}\n')
        f.write(f'#define SIGNAL_FS        {metadata["sample_rate"]}\n')
        f.write(f'#define SIGNAL_FREQ      {metadata["freq"]:.6f}f\n')
        f.write(f'#define SIGNAL_AMP       {metadata["amplitude"]:.6f}f\n')
        f.write(f'#define SIGNAL_PHASE     {metadata["phase"]:.6f}f\n')
        f.write(f'#define SIGNAL_NOISE_STD {metadata.get("noise_std", 0.0):.6f}f\n\n')

        # float signal array
        f.write(f'float32_t test_signal_float[SIGNAL_LENGTH] = {{\n')
        for i in range(samples):
            if i % 8 == 0:
                f.write('    ')
            f.write(f'{signal_float[i]:.10f}f')
            if i < samples - 1:
                f.write(', ')
            if i % 8 == 7:
                f.write('\n')
        f.write('\n};\n\n')

        # ADC raw value array
        if adc_raw is not None:
            f.write(f'uint16_t test_signal_raw[SIGNAL_LENGTH] = {{\n')
            for i in range(samples):
                if i % 16 == 0:
                    f.write('    ')
                f.write(f'{adc_raw[i]}')
                if i < samples - 1:
                    f.write(', ')
                if i % 16 == 15:
                    f.write('\n')
            f.write('\n};\n\n')

        f.write('#endif /* SIGNAL_DATA_H */\n')

    return filepath


def main():
    parser = argparse.ArgumentParser(description='generate DSP test signal')
    parser.add_argument('--waveform', default='sine',
                        choices=['sine', 'square', 'triangle'])
    parser.add_argument('--freq', type=float, default=1000.0, help='frequency (Hz)')
    parser.add_argument('--amp', type=float, default=1.0, help='amplitude (V)')
    parser.add_argument('--phase', type=float, default=0.0, help='initial phase (rad)')
    parser.add_argument('--fs', type=float, default=51200.0, help='sample rate (Hz)')
    parser.add_argument('--samples', type=int, default=1024, help='number of samples')
    parser.add_argument('--noise', type=float, default=0.0, help='noise std dev')
    parser.add_argument('--adc-bits', type=int, default=0,
                        help='ADC bit width (0=no quantization, 12, 16)')
    parser.add_argument('--vref', type=float, default=3.3, help='ADC reference voltage')
    parser.add_argument('--seed', type=int, default=20260717, help='Noise RNG seed')
    parser.add_argument('--outdir', default='test/generated', help='output directory')

    args = parser.parse_args()

    signal, adc = generate_signal(
        args.waveform, args.freq, args.amp, args.phase,
        args.fs, args.samples, args.noise, args.adc_bits, args.vref, args.seed
    )

    metadata = {
        'waveform': args.waveform,
        'freq': args.freq,
        'amplitude': args.amp,
        'phase': args.phase,
        'sample_rate': args.fs,
        'samples': args.samples,
        'noise_std': args.noise,
        'adc_bits': args.adc_bits,
        'vref': args.vref,
    }

    path = write_signal_header(signal, adc, args.outdir, metadata)
    print(f'signal file generated: {path}')
    print(f'  waveform: {args.waveform}, freq: {args.freq} Hz, '
          f'amp: {args.amp} V, fs: {args.fs} Hz, points: {args.samples}')


if __name__ == '__main__':
    main()
