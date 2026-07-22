add_executable(imds main.cpp)
target_link_libraries(imds ws2_32)
install(TARGETS imds RUNTIME DESTINATION .)
