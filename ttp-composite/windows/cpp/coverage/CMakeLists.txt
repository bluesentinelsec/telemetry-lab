set(COVERAGE_CASES
    registry_run_key
    registry_app_paths
    registry_active_setup
    registry_screensaver
    registry_runmru_delete
    startup_file
    powershell_profile
    public_binary
    double_extension_file
    double_extension_lnk
    office_startup_file
    suspicious_executable_file
    tcp_connect_2525
    tcp_connect_3389
    tcp_connect_9389
    tcp_connect_88
    tcp_connect_public_path
    dns_ip_lookup
    double_extension_execute
    creation_time_change
    ads_executable
    named_pipe_indicator
    unsigned_node_load)
foreach(case IN LISTS COVERAGE_CASES)
    add_executable(coverage_${case} ${case}/main.cpp)
    set_target_properties(coverage_${case} PROPERTIES OUTPUT_NAME ${case}
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/bin")
    target_compile_options(coverage_${case} PRIVATE -Wall -Wextra -Werror)
    target_link_libraries(coverage_${case} PRIVATE ws2_32 advapi32)
    install(TARGETS coverage_${case} RUNTIME DESTINATION coverage)
endforeach()
# Fixtures remain C binaries so their behavior does not vary with the measured
# C++ library. Live qualification stages one fixed reference set for both builds.
add_executable(windows_fixture_helper ../../c/coverage/helper.c)
add_library(windows_fixture_module SHARED ../../c/coverage/module.c)
set_target_properties(windows_fixture_module PROPERTIES PREFIX "" OUTPUT_NAME "fixture" SUFFIX ".node")
add_executable(windows_echo_server ../../c/coverage/echo_server.c)
add_executable(windows_dns_server ../../c/coverage/dns_server.c)
foreach(fixture windows_echo_server windows_dns_server)
    target_compile_options(${fixture} PRIVATE -Wall -Wextra -Werror)
    target_link_libraries(${fixture} PRIVATE ws2_32)
endforeach()
install(TARGETS windows_fixture_helper windows_fixture_module windows_echo_server windows_dns_server RUNTIME DESTINATION coverage/fixtures LIBRARY DESTINATION coverage/fixtures)
