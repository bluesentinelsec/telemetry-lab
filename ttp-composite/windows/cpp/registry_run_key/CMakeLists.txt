add_executable(registry_run_key main.cpp)
target_link_libraries(registry_run_key advapi32)
install(TARGETS registry_run_key RUNTIME DESTINATION .)
