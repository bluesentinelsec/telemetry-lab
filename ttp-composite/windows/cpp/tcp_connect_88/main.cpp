// Target rule: Uncommon Outbound Kerberos Connection
// Sigma rule ID: 322fd5f2-b5b7-1bf4-58f2-92873dc878bb
// Ruleset path: sigma/sysmon/network_connection/net_connection_win_susp_outbound_kerberos_connection.yml
#include "../internal/common.hpp"

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE tcp_connect_88" << "\n";
    if (!fixture_begin(argc,argv,"tcp_connect_88")) { Sleep(5000); return 0; }
    tcp_exchange(88);
    Sleep(5000); /* Same post-I/O lifetime in every TCP case and control. */
    success("tcp_connect_88");
    return 0;
}
