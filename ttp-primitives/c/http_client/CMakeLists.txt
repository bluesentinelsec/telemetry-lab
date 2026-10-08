add_executable(http_client main.c)
# Windows sockets live in Winsock, linked explicitly; POSIX sockets are in libc.
if(WIN32)
  target_link_libraries(http_client PRIVATE ws2_32)
endif()
install(TARGETS http_client RUNTIME DESTINATION .)
