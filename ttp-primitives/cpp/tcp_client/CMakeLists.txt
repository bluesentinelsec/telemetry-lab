add_executable(tcp_client main.cpp)
# Windows sockets live in Winsock, linked explicitly; POSIX sockets are in libc.
if(WIN32)
  target_link_libraries(tcp_client PRIVATE ws2_32)
endif()
install(TARGETS tcp_client RUNTIME DESTINATION .)
