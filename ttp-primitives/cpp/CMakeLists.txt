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

# Cross-platform primitives: built on both Linux and Windows. Each realizes one
# behavioural contract through the platform-native mechanism (/proc vs Toolhelp,
# BSD sockets vs Winsock, std::thread over pthreads vs OS threads, pipe() vs
# CreatePipe). std::-based primitives are portable as written; the raw-API ones
# branch on the platform.
add_subdirectory(process_enumeration)
add_subdirectory(thread_create)
add_subdirectory(directory_enumeration)
add_subdirectory(memory_allocate)
add_subdirectory(pipe_ipc)
add_subdirectory(tcp_client)
add_subdirectory(tcp_server)
add_subdirectory(dns_lookup)
add_subdirectory(http_client)

# Linux-only: process_exec replaces the running process image via execve, which
# has no Windows equivalent (see issue #44).
if(UNIX)
  add_subdirectory(process_exec)
endif()

add_subdirectory(tests)
