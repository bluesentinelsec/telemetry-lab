cmake_minimum_required(VERSION 3.20)

# The Windows composites are pure C WinAPI programs. They build only on Windows
# (msvcrt/ucrt substrate axis); no _WIN32 guards are needed because they are
# never compiled for any other platform.
project(ttp-composite-windows-c LANGUAGES C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

add_subdirectory(reverse_shell)
add_subdirectory(imds)
add_subdirectory(registry_run_key)
add_subdirectory(startup_folder)
