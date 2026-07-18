"""理论参考实现模块。

用 numpy/scipy 从数学原理独立实现各 DSP 算法的参考值，
不翻译 C 代码，而是基于信号处理理论公式计算。
"""

import numpy as np


# ============================================================
#  测频 — FFT 二次插值
# ============================================================

def ref_frequency_fft_interp(signal, fs):
    """FFT + 二次插值频率估计。

    数学原理：
      1. 计算信号的 FFT，取幅度谱前 N/2 点
      2. 找到幅度最大的 bin（跳过 DC）
      3. 用峰值 bin 及其左右邻点做二次插值，得到亚 bin 精度的频率
         delta = (2*k*(c+a-2b) + a - c) / (2*(c+a-2b))
         freq = delta * fs / N

    参考：fft_interp_freq.c 中 cfft_f32_fre(flag=1)
    """
    n = len(signal)
    spectrum = np.fft.fft(signal)
    mag = np.abs(spectrum[:n // 2])

    # skip DC (idx=0)
    peak_idx = int(np.argmax(mag[1:]) + 1)

    if peak_idx < 1 or peak_idx >= len(mag) - 1:
        return float(peak_idx) * fs / n

    a = mag[peak_idx - 1]
    b = mag[peak_idx]
    c = mag[peak_idx + 1]

    denom_val = 2 * (a + c - 2 * b)
    if abs(denom_val) < 1e-12:
        return float(peak_idx) * fs / n

    delta = (a - c) / denom_val
    freq = (peak_idx + delta) * fs / n
    return freq


def ref_frequency_fft_peak(signal, fs):
    """FFT 峰值频率（不做插值）。

    参考：fft_interp_freq.c 中 cfft_f32_fre(flag=2)
    """
    n = len(signal)
    spectrum = np.fft.fft(signal)
    mag = np.abs(spectrum[:n // 2])
    peak_idx = int(np.argmax(mag[1:]) + 1)
    return float(peak_idx) * fs / n


# ============================================================
#  测频 — 过零检测
# ============================================================

def ref_frequency_zero_cross(signal, fs):
    """过零检测频率估计（多周期平均法）。

    数学原理：
      1. 寻找所有正向过零点（前一采样 ≤ 0 且 当前采样 > 0）
      2. 每个过零点用线性插值精确到亚采样位置
      3. 用首个和末个过零点的时间差除以期间完整周期数，得平均周期
      4. freq = 1 / avg_period

    参考：zero_cross.c 中 ZeroCross_Freq()
    """
    n = len(signal)
    crossings = []
    for i in range(1, n):
        if signal[i - 1] <= 0 < signal[i]:
            denom = signal[i] - signal[i - 1]
            if abs(denom) < 1e-12:
                frac = 0.0
            else:
                frac = -signal[i - 1] / denom
            crossings.append(float(i - 1) + frac)

    if len(crossings) < 2:
        return 0.0

    total_time = (crossings[-1] - crossings[0]) / fs
    periods = len(crossings) - 1
    return float(periods) / total_time


def ref_frequency_zero_cross_period(signal, fs):
    """过零检测周期测量（对所有完整周期取平均）。

    参考：zero_cross.c 中 ZeroCross_Period()
    """
    n = len(signal)
    crossings = []
    for i in range(1, n):
        if signal[i - 1] <= 0 < signal[i]:
            denom = signal[i] - signal[i - 1]
            if abs(denom) < 1e-12:
                frac = 0.0
            else:
                frac = -signal[i - 1] / denom
            t = float(i - 1) + frac
            crossings.append(t)

    if len(crossings) < 2:
        return 0.0

    period_samples = (crossings[-1] - crossings[0]) / (len(crossings) - 1)
    return period_samples / fs


# ============================================================
#  测幅 — RMS 法
# ============================================================

def ref_amplitude_rms_sine(signal):
    """正弦波 RMS 幅度。

    数学原理：正弦波的 RMS = A / sqrt(2)，所以 A = sqrt(2) * RMS
    先减直流分量，再算 RMS，最后乘 sqrt(2)。

    参考：rms_amplitude.c 中 Measuring_Sine_Amplitude()
    """
    dc = np.mean(signal)
    x = signal - dc
    rms = np.sqrt(np.mean(x * x))
    return rms * np.sqrt(2)


def ref_amplitude_rms_square(signal):
    """方波 RMS 幅度。方波 RMS = 峰值幅度。"""
    dc = np.mean(signal)
    x = signal - dc
    rms = np.sqrt(np.mean(x * x))
    return rms


def ref_amplitude_rms_triangle(signal):
    """三角波 RMS 幅度。三角波 RMS * sqrt(3) = 峰值。"""
    dc = np.mean(signal)
    x = signal - dc
    rms = np.sqrt(np.mean(x * x))
    return rms * np.sqrt(3)


# ============================================================
#  测相 — IQ 正交解调
# ============================================================

def ref_phase_iq(freq, fs, signal):
    """IQ 正交解调相位估计。

    数学原理：
      1. 生成与待测信号同频的 I 路 (cos) 和 Q 路 (sin) 参考信号
      2. 信号减直流后分别与 I/Q 做内积（相关）
      3. 对 x=A*sin(wt+phase)，phase = atan2(I_sum, Q_sum)

    参考：iq_phase.c 中 CalPhase()
    """
    n = len(signal)
    dc = np.mean(signal)
    x = signal - dc

    samples_per_cycle = int(fs / freq)
    if samples_per_cycle < 1:
        return 0.0
    k = n // samples_per_cycle
    n_used = k * samples_per_cycle
    if n_used < samples_per_cycle:
        return 0.0

    x = x[:n_used]
    n_used = len(x)

    t = np.arange(n_used, dtype=np.float64) / fs
    ref_i = np.cos(2 * np.pi * freq * t)
    ref_q = np.sin(2 * np.pi * freq * t)

    i_sum = np.dot(x.astype(np.float64), ref_i)
    q_sum = np.dot(x.astype(np.float64), ref_q)

    return float(np.arctan2(i_sum, q_sum))


# ============================================================
#  CZT — Chirp Z 变换频谱细化
# ============================================================

def ref_czt(signal, fs, f_start, f_end, n_points):
    """Chirp Z 变换频谱细化。

    数学原理：
      CZT 在单位圆的指定弧段上计算 Z 变换。
      z_k = A * W^(-k)
      A = exp(j*2π*f_start/fs)
      W = exp(-j*2π*(f_end-f_start)/(fs*(M-1)))

    直接实现（非 FFT 加速版），用于参考验证。

    Returns:
        (freqs, magnitudes): 频率轴和对应的幅度谱
    """
    n = len(signal)
    m = n_points
    w_start = 2 * np.pi * f_start / fs
    w_end = 2 * np.pi * f_end / fs
    delta_w = (w_end - w_start) / (m - 1)

    k = np.arange(m)
    z_pow = np.exp(-1j * (w_start + delta_w * k))  # A * W^(-k) 简化形式

    # 对每个输出点计算 CZT
    magnitudes = np.zeros(m)
    n_arr = np.arange(n)
    for i in range(m):
        # z_k = exp(j * (w_start + delta_w * i))
        z_i = 1j * (w_start + delta_w * i)
        exp_terms = np.exp(-z_i * n_arr)
        czt_val = np.dot(signal, exp_terms)
        magnitudes[i] = np.abs(czt_val)

    freqs = f_start + np.arange(m) * (f_end - f_start) / (m - 1)
    return freqs, magnitudes


def ref_czt_freq(signal, fs, f_start, f_end, n_points):
    """CZT 峰值频率估计。"""
    freqs, mags = ref_czt(signal, fs, f_start, f_end, n_points)
    peak_idx = int(np.argmax(mags))
    return float(freqs[peak_idx])


def ref_czt_amp(signal, fs, f_start, f_end, n_points):
    """CZT 峰值幅度估计。"""
    _, mags = ref_czt(signal, fs, f_start, f_end, n_points)
    n = len(signal)
    peak_mag = float(np.max(mags))
    # 幅度归一化（与 czt_zoom_fft.c 一致：mag / N * 2）
    return peak_mag / n * 2
