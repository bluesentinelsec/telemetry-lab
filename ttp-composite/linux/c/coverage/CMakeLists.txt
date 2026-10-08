# One source entry point and one executable per measured composite.
set(COVERAGE_CASES
    identity_change
    interactive_recon
    netcat_exec
    bulk_clear
    ssh_nonstandard
    shell_network
    proxy_environment
    network_tool
    remote_copy
    ingress_copy
    privileged_mount
    privileged_debugfs
    k8s_client
    protected_shell
    web_shell
    web_child
    web_reverse_shell
    npm_network_tool
    shell_config_read
    hidden_file
    executable_chmod
    executable_create
    nodeport_exchange
    miner_port_exchange
    unexpected_inbound
    rpm_database_write
    namespace_setns
    namespace_unshare_denied
    userfaultfd_create
    bpf_program_load
    release_agent_write
    host_path_read
    search_private_keys
    search_aws_credentials
    decode_base64
    package_manager_query
    glibc_tunable_child
    traversal_read
    sensitive_read
    log_truncate
    sensitive_symlink
    sensitive_hardlink
    packet_socket
    reverse_shell
    ptrace_attach
    ptrace_traceme
    exec_shm
    drop_execute
    memfd_execute
    shell_config_write
    cron_write
    ssh_read
    udp_exchange
    dev_file
    metadata_ec2
    metadata_cloud
    history_truncate
    setid_mode
    proc_environ
    authorized_keys
    repository_write
    binary_write
    monitored_write
    etc_write
    root_write
    binary_rename
    binary_mkdir
    negative
)
foreach(case IN LISTS COVERAGE_CASES)
    add_executable(coverage_${case} ${case}/main.c)
    set_target_properties(coverage_${case} PROPERTIES OUTPUT_NAME ${case}
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/bin")
    target_compile_definitions(coverage_${case} PRIVATE _GNU_SOURCE)
    target_compile_options(coverage_${case} PRIVATE -Wall -Wextra -Werror)
    install(TARGETS coverage_${case} RUNTIME DESTINATION coverage)
endforeach()
add_executable(fixture_prepare fixture_prepare.c)
target_compile_definitions(fixture_prepare PRIVATE _GNU_SOURCE)
target_compile_options(fixture_prepare PRIVATE -Wall -Wextra -Werror)
install(TARGETS fixture_prepare RUNTIME DESTINATION coverage)
