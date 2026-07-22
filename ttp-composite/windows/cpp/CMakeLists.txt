cmake_minimum_required(VERSION 3.20)

# The Windows composites are WinAPI programs built only on Windows (the C++
# libstdc++/libc++ substrate axis); no _WIN32 guards are needed because they are
# never compiled for any other platform. Composites are detection-focused, so
# unlike the primitives they carry no C++ standard-library substrate anchor --
# the measured effect is the emitted Sysmon event, not the runtime.
project(ttp-composite-windows-cpp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_subdirectory(reverse_shell)
add_subdirectory(imds)
add_subdirectory(registry_run_key)
add_subdirectory(startup_folder)
