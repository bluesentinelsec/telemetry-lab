cmake_minimum_required(VERSION 3.20)
project(ttp-composite-cpp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Composites are validated by detonation (does the shipped Falco rule fire?),
# not by unit tests -- so there is no Catch2 fetch and no enable_testing() here.
# Each composite is a self-contained, benign ATT&CK technique that installs into
# a flat bundle for substrate verification on the lab.
add_subdirectory(reverse_shell)
add_subdirectory(imds)
add_subdirectory(read_sensitive_file)
add_subdirectory(symlink_sensitive)
add_subdirectory(clear_log)
add_subdirectory(mkdir_bin)
add_subdirectory(ptrace_antidebug)
