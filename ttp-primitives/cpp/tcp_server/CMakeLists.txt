add_executable(tcp_server main.cpp)
# Windows sockets live in Winsock, linked explicitly; POSIX sockets are in libc.
if(WIN32)
  target_link_libraries(tcp_server PRIVATE ws2_32)
endif()
install(TARGETS tcp_server RUNTIME DESTINATION .)
