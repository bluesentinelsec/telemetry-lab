cmake_minimum_required(VERSION 3.20)
project(tmon LANGUAGES C CXX)

# -----------------------------------------------------------------------------
# tmon-linux — process-scoped telemetry monitor (eBPF). Three source layers:
#   src/model  (1) data model      — plain value types
#   src/core   (2) business logic   — capture engine, syscall names
#   src/view   (3) presentation     — human + JSON formatters
# The BPF program (bpf/) is compiled with clang to a CO-RE object and turned into
# a libbpf skeleton header that the engine embeds.
# -----------------------------------------------------------------------------

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_C_STANDARD 11)
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

# --- Vendored, compiled-in dependencies (network fetch, pinned) --------------
# CLI11 is a single header; cJSON is a single .c. Both are small and unlikely to
# be present on a default Debian host, so they are built into the binary rather
# than linked dynamically.
include(FetchContent)
set(FETCHCONTENT_QUIET OFF)

FetchContent_Declare(cli11
  GIT_REPOSITORY https://github.com/CLIUtils/CLI11.git
  GIT_TAG v2.4.2)
set(CLI11_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(CLI11_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)

FetchContent_Declare(cjson
  GIT_REPOSITORY https://github.com/DaveGamble/cJSON.git
  GIT_TAG v1.7.18)
set(ENABLE_CJSON_TEST OFF CACHE BOOL "" FORCE)
set(CJSON_BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)

FetchContent_MakeAvailable(cli11 cjson)

# --- Tools needed to build the BPF object and skeleton -----------------------
find_program(CLANG_EXE clang REQUIRED)
find_program(BPFTOOL_EXE bpftool REQUIRED)

# libbpf: headers + static archive. libbpf-dev ships both on Debian.
find_path(LIBBPF_INCLUDE_DIR bpf/libbpf.h REQUIRED)
find_library(LIBBPF_STATIC NAMES libbpf.a REQUIRED)

set(GEN_DIR ${CMAKE_BINARY_DIR}/gen)
file(MAKE_DIRECTORY ${GEN_DIR})

# --- Step 1: vmlinux.h from the running kernel's BTF -------------------------
add_custom_command(
  OUTPUT ${GEN_DIR}/vmlinux.h
  COMMAND ${BPFTOOL_EXE} btf dump file /sys/kernel/btf/vmlinux format c
          > ${GEN_DIR}/vmlinux.h
  COMMENT "Generating vmlinux.h from kernel BTF"
  VERBATIM)

# --- Step 2: compile the BPF program to a CO-RE object -----------------------
set(BPF_SRC ${CMAKE_SOURCE_DIR}/bpf/tmon.bpf.c)
set(BPF_OBJ ${GEN_DIR}/tmon.bpf.o)
add_custom_command(
  OUTPUT ${BPF_OBJ}
  COMMAND ${CLANG_EXE} -g -O2 -target bpf -D__TARGET_ARCH_x86
          -I${GEN_DIR} -I${CMAKE_SOURCE_DIR}/bpf -I${LIBBPF_INCLUDE_DIR}
          -c ${BPF_SRC} -o ${BPF_OBJ}
  DEPENDS ${BPF_SRC} ${GEN_DIR}/vmlinux.h
          ${CMAKE_SOURCE_DIR}/bpf/tmon_event.h
  COMMENT "Compiling BPF program tmon.bpf.c"
  VERBATIM)

# --- Step 3: generate the libbpf skeleton header -----------------------------
add_custom_command(
  OUTPUT ${GEN_DIR}/tmon.skel.h
  COMMAND ${BPFTOOL_EXE} gen skeleton ${BPF_OBJ} > ${GEN_DIR}/tmon.skel.h
  DEPENDS ${BPF_OBJ}
  COMMENT "Generating BPF skeleton tmon.skel.h"
  VERBATIM)

# --- Step 4: generate the syscall-number -> name table -----------------------
add_custom_command(
  OUTPUT ${GEN_DIR}/syscall_table.generated.h
  COMMAND ${CMAKE_COMMAND} -E env CC=${CMAKE_C_COMPILER}
          bash ${CMAKE_SOURCE_DIR}/cmake/gen_syscalls.sh
          > ${GEN_DIR}/syscall_table.generated.h
  DEPENDS ${CMAKE_SOURCE_DIR}/cmake/gen_syscalls.sh
  COMMENT "Generating syscall name table"
  VERBATIM)

add_custom_target(tmon_generated DEPENDS
  ${GEN_DIR}/tmon.skel.h
  ${GEN_DIR}/syscall_table.generated.h)

# --- The tmon executable -----------------------------------------------------
add_executable(tmon
  cli/main.cpp
  src/core/engine.cpp
  src/core/syscall_names.cpp
  src/view/human_formatter.cpp
  src/view/json_formatter.cpp)
add_dependencies(tmon tmon_generated)

target_include_directories(tmon PRIVATE
  ${CMAKE_SOURCE_DIR}/src   # model/, core/, view/ headers
  ${CMAKE_SOURCE_DIR}       # bpf/tmon_event.h
  ${GEN_DIR}                # tmon.skel.h, syscall_table.generated.h
  ${cjson_SOURCE_DIR}       # cJSON.h (FetchContent does not export it)
  ${LIBBPF_INCLUDE_DIR})

target_compile_options(tmon PRIVATE -Wall -Wextra)

# Dependency strategy. glibc stays dynamic (present everywhere). libbpf is the
# one library a bare Debian host is unlikely to have, so it is linked as a static
# archive (must precede libelf/libz on the line so its references resolve).
# libelf and libz are linked dynamically: static libelf.a on Debian drags in
# unpackaged elfutils-internal symbols, and both shared libs are either universal
# (zlib) or a one-package install (libelf1). libstdc++/libgcc are statically
# bound; CLI11 and cJSON are compiled in.
target_link_libraries(tmon PRIVATE
  CLI11::CLI11
  cjson
  ${LIBBPF_STATIC}
  elf
  z)
target_link_options(tmon PRIVATE -static-libstdc++ -static-libgcc)

install(TARGETS tmon RUNTIME DESTINATION bin)
