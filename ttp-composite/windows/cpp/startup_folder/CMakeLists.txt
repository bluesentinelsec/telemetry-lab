add_executable(startup_folder main.cpp)
target_link_libraries(startup_folder shell32)
install(TARGETS startup_folder RUNTIME DESTINATION .)
