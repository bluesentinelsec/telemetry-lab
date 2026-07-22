// imds composite (T1552.005, Unsecured Credentials: Cloud Instance Metadata API).
//
// Detection target: Sysmon EID 3 (network connection); the shipped Sigma rule
// keys on a connection to the cloud metadata endpoint 169.254.169.254. The
// behaviour is a single outbound TCP connect to that link-local address on
// port 80. Expected robust across the Windows substrate matrix: Sysmon records
// the connection tuple (the event-level fact), never the Winsock call path
// where substrate differences would live.
//
// Benign: the connect is attempted and the socket closed immediately; nothing
// is sent and no credentials are read. On a host without a metadata service
// the connect simply fails -- the network-connect telemetry is emitted on the
// attempt regardless. Exits 0.
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>

int main() {
    WSADATA wsa;
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) {
        return 1;
    }

    SOCKET s = socket(AF_INET, SOCK_STREAM, 0);
    if (s != INVALID_SOCKET) {
        struct sockaddr_in addr;
        ZeroMemory(&addr, sizeof addr);
        addr.sin_family = AF_INET;
        addr.sin_port = htons(80);
        addr.sin_addr.s_addr = inet_addr("169.254.169.254");
        connect(s, (struct sockaddr *)&addr, sizeof addr);
        closesocket(s);
    }

    WSACleanup();
    return 0;
}
