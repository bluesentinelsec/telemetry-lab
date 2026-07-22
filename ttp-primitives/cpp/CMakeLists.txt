cmake_minimum_required(VERSION 3.20)
project(ttp-primitives-cpp LANGUAGES CXX)

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

# Linux-first primitives (the 8 Linux configs). Gated out of Windows builds:
# several use POSIX-only mechanisms (execve, /proc, anonymous pipes, BSD
# sockets) whose Windows equivalents are tracked separately (issue #44).
if(UNIX)
  add_subdirectory(process_exec)
  add_subdirectory(process_enumeration)
  add_subdirectory(thread_create)
  add_subdirectory(directory_enumeration)
  add_subdirectory(memory_allocate)
  add_subdirectory(pipe_ipc)
  add_subdirectory(tcp_client)
  add_subdirectory(tcp_server)
  add_subdirectory(dns_lookup)
  add_subdirectory(http_client)
endif()

add_subdirectory(tests)
