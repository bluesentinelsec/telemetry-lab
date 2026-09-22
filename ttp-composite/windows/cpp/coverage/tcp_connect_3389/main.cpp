#include "../common.hpp"

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE tcp_connect_3389" << "\n";
    if (!fixture_begin(argc,argv,"tcp_connect_3389")) { Sleep(5000); return 0; }
    socket_start();
    SOCKET s=connect_local(3389);
    /* Minimal X.224 connection request: no credentials or RDP session.
       The target rule tests the connection metadata, not these bytes. */
    const char request[]={3,0,0,11,6,(char)0xe0,0,0,0,0,0};
    socket_send_all(s,request,sizeof request);
    CHECK(closesocket(s)==0); CHECK(WSACleanup()==0);
    Sleep(5000); /* Same post-I/O lifetime in every TCP case and control. */
    success("tcp_connect_3389");
    return 0;
}
