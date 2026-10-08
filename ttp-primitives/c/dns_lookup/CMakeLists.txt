add_executable(dns_lookup main.c)
# Windows sockets live in Winsock, linked explicitly; POSIX sockets are in libc.
if(WIN32)
  target_link_libraries(dns_lookup PRIVATE ws2_32)
endif()
install(TARGETS dns_lookup RUNTIME DESTINATION .)
