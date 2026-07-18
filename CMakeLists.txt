cmake_minimum_required(VERSION 3.16)
project(DSP_Algorithm_Lib C)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

# 关闭 CMSIS-DSP 中可能产生的大量 warning
if(CMAKE_C_COMPILER_ID STREQUAL "GNU")
    add_compile_options(-Wno-unused-variable -Wno-unused-but-set-variable -Wno-builtin-macro-redefined)
elseif(CMAKE_C_COMPILER_ID STREQUAL "MSVC")
    add_compile_options(/wd4101 /wd4189)
endif()

# PC 端验证使用 CMSIS-DSP 的 HOST 模式，不依赖额外的 CMSIS-Core 仓库。
set(HOST ON CACHE BOOL "Build CMSIS-DSP for the local host" FORCE)
set(FASTBUILD ON CACHE BOOL "Use CMSIS-DSP aggregate sources" FORCE)
set(CMSISDSP_INSTALL OFF CACHE BOOL "Disable CMSIS-DSP install" FORCE)
set(WRAPPER ON CACHE BOOL "Enable deprecated wrapper functions" FORCE)
add_subdirectory(external/CMSIS-DSP/Source)

add_subdirectory(test)
