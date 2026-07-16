include(Catch)

# One Catch2 suite for all C primitives. To add a primitive: add its test source
# here, and pass the path of its built binary as a compile definition below.
add_executable(c-primitive-tests
  empty_test.cpp
  file_io_test.cpp
  spawn_test.cpp
)

target_link_libraries(c-primitive-tests PRIVATE Catch2::Catch2WithMain)
target_include_directories(c-primitive-tests PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/../../testing)

target_compile_definitions(c-primitive-tests PRIVATE
  EMPTY_BIN="$<TARGET_FILE:empty>"
  FILE_IO_BIN="$<TARGET_FILE:file_io>"
  SPAWN_BIN="$<TARGET_FILE:spawn>"
)

# The suite spawns the primitives, so they must exist before it runs.
add_dependencies(c-primitive-tests empty file_io spawn)

catch_discover_tests(c-primitive-tests)
