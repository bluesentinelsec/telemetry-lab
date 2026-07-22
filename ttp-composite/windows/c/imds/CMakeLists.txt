add_executable(imds main.c)
target_link_libraries(imds ws2_32)
install(TARGETS imds RUNTIME DESTINATION .)
