include(Catch)

# One Catch2 suite for all C++ primitives. To add a primitive: add its test
# source and its built-binary path (as a compile definition) below. The
# Linux-first primitives are gated behind UNIX to match the build in
# ../CMakeLists.txt.
set(CPP_PRIMITIVE_TEST_SOURCES
  empty_test.cpp
  file_io_test.cpp
  spawn_test.cpp
)
set(CPP_PRIMITIVE_TARGETS empty file_io spawn)

if(UNIX)
  list(APPEND CPP_PRIMITIVE_TEST_SOURCES
    process_exec_test.cpp
    process_enumeration_test.cpp
    thread_create_test.cpp
    directory_enumeration_test.cpp
    memory_allocate_test.cpp
    pipe_ipc_test.cpp
    tcp_client_test.cpp
    tcp_server_test.cpp
    dns_lookup_test.cpp
    http_client_test.cpp
  )
  list(APPEND CPP_PRIMITIVE_TARGETS
    process_exec process_enumeration thread_create directory_enumeration
    memory_allocate pipe_ipc tcp_client tcp_server dns_lookup http_client
  )
endif()

add_executable(cpp-primitive-tests ${CPP_PRIMITIVE_TEST_SOURCES})

target_link_libraries(cpp-primitive-tests PRIVATE Catch2::Catch2WithMain)
target_include_directories(cpp-primitive-tests PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/../../testing)

target_compile_definitions(cpp-primitive-tests PRIVATE
  EMPTY_BIN="$<TARGET_FILE:empty>"
  FILE_IO_BIN="$<TARGET_FILE:file_io>"
  SPAWN_BIN="$<TARGET_FILE:spawn>"
)

if(UNIX)
  target_compile_definitions(cpp-primitive-tests PRIVATE
    PROCESS_EXEC_BIN="$<TARGET_FILE:process_exec>"
    PROCESS_ENUMERATION_BIN="$<TARGET_FILE:process_enumeration>"
    THREAD_CREATE_BIN="$<TARGET_FILE:thread_create>"
    DIRECTORY_ENUMERATION_BIN="$<TARGET_FILE:directory_enumeration>"
    MEMORY_ALLOCATE_BIN="$<TARGET_FILE:memory_allocate>"
    PIPE_IPC_BIN="$<TARGET_FILE:pipe_ipc>"
    TCP_CLIENT_BIN="$<TARGET_FILE:tcp_client>"
    TCP_SERVER_BIN="$<TARGET_FILE:tcp_server>"
    DNS_LOOKUP_BIN="$<TARGET_FILE:dns_lookup>"
    HTTP_CLIENT_BIN="$<TARGET_FILE:http_client>"
  )
endif()

# The suite spawns the primitives, so they must exist before it runs.
add_dependencies(cpp-primitive-tests ${CPP_PRIMITIVE_TARGETS})

catch_discover_tests(cpp-primitive-tests)
