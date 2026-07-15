include(Catch)

# One Catch2 suite over tmon_core — the kernel-independent logic. The BPF engine
# (spawn + verifier + ring buffer) needs a real kernel and root, so it is not
# unit-tested here; it is exercised by running tmon on a live host.
add_executable(tmon-tests
  syscall_names_test.cpp
  errno_names_test.cpp
  event_decode_test.cpp
  meta_parse_test.cpp
  human_formatter_test.cpp
  json_formatter_test.cpp)

target_link_libraries(tmon-tests PRIVATE tmon_core Catch2::Catch2WithMain)

catch_discover_tests(tmon-tests)
