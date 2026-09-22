cmake_minimum_required(VERSION 3.20)

# One executable per case. The expanded coverage suite uses the selected C++
# library for standard I/O and strings, with native WinAPI where C++17 has no
# equivalent (registry, sockets, process creation and other Windows objects).
project(ttp-composite-windows-cpp LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_subdirectory(reverse_shell)
add_subdirectory(imds)
add_subdirectory(registry_run_key)
add_subdirectory(startup_folder)

add_subdirectory(coverage)
