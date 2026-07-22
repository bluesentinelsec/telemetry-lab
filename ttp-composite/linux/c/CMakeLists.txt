cmake_minimum_required(VERSION 3.20)

# The Linux C composites. Unlike the primitives, composites carry no unit-test
# harness: they are ATT&CK techniques validated by whether a shipped Falco rule
# fires when they detonate in a container, not by an exit-code assertion.
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
