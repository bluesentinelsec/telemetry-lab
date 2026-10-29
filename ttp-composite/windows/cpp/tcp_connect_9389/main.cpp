// Target rule: Uncommon Connection to Active Directory Web Services
// Sigma rule ID: ae8c1c58-4743-c0c8-3b30-7d69f7cbee68
// Ruleset path: sigma/sysmon/network_connection/net_connection_win_adws_unusual_connection.yml
#include "../internal/common.hpp"

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE tcp_connect_9389" << "\n";
    if (!fixture_begin(argc,argv,"tcp_connect_9389")) { Sleep(5000); return 0; }
    tcp_exchange(9389);
    Sleep(5000); /* Same post-I/O lifetime in every TCP case and control. */
    success("tcp_connect_9389");
    return 0;
}
