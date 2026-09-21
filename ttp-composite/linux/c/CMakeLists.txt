cmake_minimum_required(VERSION 3.20)

# Linux C composites, including the independently verified Falco coverage suite.
project(ttp-composite-c LANGUAGES C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

add_subdirectory(reverse_shell)
add_subdirectory(imds)
add_subdirectory(read_sensitive_file)
add_subdirectory(symlink_sensitive)
add_subdirectory(clear_log)
add_subdirectory(mkdir_bin)
add_subdirectory(ptrace_antidebug)

add_subdirectory(coverage)
