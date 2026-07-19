# 头文件搜索路径：所有算法源码目录 + 生成信号目录
set(ALGO_SRC_DIR ${CMAKE_SOURCE_DIR})

include_directories(
    ${ALGO_SRC_DIR}/测频/FFT实现
    ${ALGO_SRC_DIR}/测频/FFT二次插值测频
    ${ALGO_SRC_DIR}/测频/过零比较测频
    ${ALGO_SRC_DIR}/测幅/均方根测幅
    ${ALGO_SRC_DIR}/测幅/差分三角波测幅
    ${ALGO_SRC_DIR}/测幅/平顶窗FFT测幅
    ${ALGO_SRC_DIR}/测幅/CZT频谱细化
    ${ALGO_SRC_DIR}/测相/正交解调测相
    ${ALGO_SRC_DIR}/测相/FIR滤波
    ${ALGO_SRC_DIR}/backend
    ${CMAKE_CURRENT_SOURCE_DIR}/generated
)

# ---- Sanity test (CMSIS-DSP linkage check) ----
add_executable(test_sanity test_runner/test_sanity.c)
target_link_libraries(test_sanity CMSISDSP m)

# ---- Frequency measurement test runner ----
add_executable(test_frequency
    test_runner/test_frequency.c
    ${ALGO_SRC_DIR}/测频/FFT实现/fft_n.c
    ${ALGO_SRC_DIR}/测频/FFT二次插值测频/fft_interp_freq.c
    ${ALGO_SRC_DIR}/测频/过零比较测频/zero_cross.c
)
target_link_libraries(test_frequency CMSISDSP m)

# ---- Direct FFT-core validation runner ----
add_executable(test_fft_core
    test_runner/test_fft_core.c
    ${ALGO_SRC_DIR}/测频/FFT实现/fft_n.c
)
target_link_libraries(test_fft_core CMSISDSP m)

# ---- Amplitude measurement test runner ----
add_executable(test_amplitude
    test_runner/test_amplitude.c
    ${ALGO_SRC_DIR}/测幅/均方根测幅/rms_amplitude.c
)
target_link_libraries(test_amplitude CMSISDSP m)

# ---- Legacy I/Q amplitude helper validation runner ----
add_executable(test_mag_phase
    test_runner/test_mag_phase.c
    ${ALGO_SRC_DIR}/测相/正交解调测相/mag_phase.c
)
target_link_libraries(test_mag_phase CMSISDSP m)

# ---- Phase measurement test runner ----
add_executable(test_phase
    test_runner/test_phase.c
    ${ALGO_SRC_DIR}/测相/正交解调测相/fft_buffer.c
    ${ALGO_SRC_DIR}/测相/正交解调测相/iq_phase.c
)
target_link_libraries(test_phase CMSISDSP m)

# ---- CZT spectrum refinement test runner ----
add_executable(test_czt
    test_runner/test_czt.c
    ${ALGO_SRC_DIR}/测幅/CZT频谱细化/czt_zoom_fft.c
)
target_link_libraries(test_czt CMSISDSP m)

# ---- FIR response validation runner ----
add_executable(test_fir_response
    test_runner/test_fir_response.c
    ${ALGO_SRC_DIR}/测相/FIR滤波/fir_filter.c
)
target_link_libraries(test_fir_response CMSISDSP m)

# ---- Fixed-size wrapper safety regression runner ----
add_executable(test_safety
    test_runner/test_safety.c
    ${ALGO_SRC_DIR}/测相/正交解调测相/fft_buffer.c
    ${ALGO_SRC_DIR}/测相/正交解调测相/iq_phase.c
    ${ALGO_SRC_DIR}/测相/FIR滤波/fir_filter.c
)
target_link_libraries(test_safety CMSISDSP m)

# Apply optimization only to locally owned test executables, never CMSIS-DSP.
if(CMAKE_C_COMPILER_ID STREQUAL "GNU")
    foreach(test_target
            test_sanity
            test_frequency
            test_fft_core
            test_amplitude
            test_mag_phase
            test_phase
            test_czt
            test_fir_response
            test_safety)
        target_compile_options(${test_target} PRIVATE -O2)
    endforeach()
endif()
