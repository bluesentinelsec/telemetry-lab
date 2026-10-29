// Target rule: Suspicious Outbound SMTP Connections
// Sigma rule ID: f8a59cdc-b3d1-8f59-c3f4-4db6d94e8efc
// Ruleset path: sigma/sysmon/network_connection/net_connection_win_susp_outbound_smtp_connections.yml
#include "../internal/common.h"

int main(int argc, char **argv) {
    puts("COMPOSITE_CASE tcp_connect_2525");
    if (!fixture_begin(argc,argv,"tcp_connect_2525")) { Sleep(5000); return 0; }
    tcp_exchange(2525);
    Sleep(5000); /* Same post-I/O lifetime in every TCP case and control. */
    success("tcp_connect_2525");
    return 0;
}
