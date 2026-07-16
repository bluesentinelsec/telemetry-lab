cmake_minimum_required(VERSION 3.20)

# The primitives are pure C. CXX is enabled only for the Catch2 test suite,
# which is C++; it is a harness, not an artifact under measurement.
project(ttp-primitives-c LANGUAGES C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)
FetchContent_Declare(
  Catch2
  GIT_REPOSITORY https://github.com/catchorg/Catch2.git
  GIT_TAG v3.7.1
)
FetchContent_MakeAvailable(Catch2)
list(APPEND CMAKE_MODULE_PATH ${catch2_SOURCE_DIR}/extras)

enable_testing()

add_subdirectory(empty)
add_subdirectory(file_io)
add_subdirectory(spawn)
add_subdirectory(tests)
