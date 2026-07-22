add_executable(reverse_shell main.c)
target_link_libraries(reverse_shell ws2_32)
install(TARGETS reverse_shell RUNTIME DESTINATION .)
