# 头文件搜索路径：所有算法源码目录 + 生成信号目录
set(ALGO_SRC_DIR ${CMAKE_SOURCE_DIR})

include_directories(
    ${ALGO_SRC_DIR}/freq_measure/fft
    ${ALGO_SRC_DIR}/freq_measure/fft_interp_freq
    ${ALGO_SRC_DIR}/freq_measure/zero_cross_freq
    ${ALGO_SRC_DIR}/amp_measure/rms
    ${ALGO_SRC_DIR}/amp_measure/diff_tri_amp
    ${ALGO_SRC_DIR}/amp_measure/flattop_fft
    ${ALGO_SRC_DIR}/amp_measure/czt
    ${ALGO_SRC_DIR}/phase_measure/iq_demod
    ${ALGO_SRC_DIR}/phase_measure/fir_filter
    ${ALGO_SRC_DIR}/backend
    ${CMAKE_CURRENT_SOURCE_DIR}/generated
)

# ---- Sanity test (CMSIS-DSP linkage check) ----
add_executable(test_sanity test_runner/test_sanity.c)
target_link_libraries(test_sanity CMSISDSP m)

# ---- Frequency measurement test runner ----
add_executable(test_frequency
    test_runner/test_frequency.c
    ${ALGO_SRC_DIR}/freq_measure/fft/fft_n.c
    ${ALGO_SRC_DIR}/freq_measure/fft_interp_freq/fft_interp_freq.c
    ${ALGO_SRC_DIR}/freq_measure/zero_cross_freq/zero_cross.c
)
target_link_libraries(test_frequency CMSISDSP m)

# ---- Amplitude measurement test runner ----
add_executable(test_amplitude
    test_runner/test_amplitude.c
    ${ALGO_SRC_DIR}/amp_measure/rms/rms_amplitude.c
)
target_link_libraries(test_amplitude CMSISDSP m)

# ---- Phase measurement test runner ----
add_executable(test_phase
    test_runner/test_phase.c
    ${ALGO_SRC_DIR}/phase_measure/iq_demod/fft_buffer.c
    ${ALGO_SRC_DIR}/phase_measure/iq_demod/iq_phase.c
)
target_link_libraries(test_phase CMSISDSP m)

# ---- CZT spectrum refinement test runner ----
add_executable(test_czt
    test_runner/test_czt.c
    ${ALGO_SRC_DIR}/amp_measure/czt/czt_zoom_fft.c
)
target_link_libraries(test_czt CMSISDSP m)

# ---- Fixed-size wrapper safety regression runner ----
add_executable(test_safety
    test_runner/test_safety.c
    ${ALGO_SRC_DIR}/phase_measure/iq_demod/fft_buffer.c
    ${ALGO_SRC_DIR}/phase_measure/iq_demod/iq_phase.c
    ${ALGO_SRC_DIR}/phase_measure/fir_filter/fir_filter.c
)
target_link_libraries(test_safety CMSISDSP m)
