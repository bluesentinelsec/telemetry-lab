#pragma once
#include "common.h"
static inline struct sockaddr_in address(const char *ip, unsigned short port) {
    struct sockaddr_in a = {.sin_family=AF_INET, .sin_port=htons(port)};
    CHECK(inet_pton(AF_INET, ip, &a.sin_addr) == 1); return a;
}
static inline void tcp_exchange(const char *ip, int shell) {
    int lst = socket(AF_INET, SOCK_STREAM, 0); CHECK(lst >= 0);
    struct sockaddr_in a=address(ip, shell ? 4444 : 80);
    CHECK(bind(lst, (struct sockaddr *)&a, sizeof(a)) == 0); CHECK(listen(lst, 1) == 0);
    int srv;
    if (shell) {
        pid_t pid=fork(); CHECK(pid >= 0);
        if (pid == 0) {
            CHECK(close(lst) == 0);
            int cli=socket(AF_INET, SOCK_STREAM, 0); CHECK(cli >= 0);
            CHECK(connect(cli, (struct sockaddr *)&a, sizeof(a)) == 0);
            for (int i=0;i<3;++i) CHECK(dup2(cli,i) >= 0);
            if (cli > 2) close(cli);
            execl("/bin/sh", "sh", (char *)NULL); _exit(127);
        }
        srv=accept(lst, NULL, NULL); CHECK(srv >= 0); CHECK(close(lst) == 0);
        const char command[]="printf 'SHELL_OK\\n'; exit\n";
        write_all(srv,command,sizeof(command)-1);
        char buf[256]={0}; ssize_t used=0,n;
        while (used < (ssize_t)sizeof(buf)-1 && (n=read(srv,buf+used,sizeof(buf)-1-(size_t)used)) > 0) used+=n;
        CHECK(strstr(buf,"SHELL_OK\n") != NULL); child_ok(pid);
    } else {
        int cli=socket(AF_INET, SOCK_STREAM, 0); CHECK(cli >= 0);
        CHECK(connect(cli, (struct sockaddr *)&a, sizeof(a)) == 0);
        srv=accept(lst, NULL, NULL); CHECK(srv >= 0); CHECK(close(lst) == 0);
        char buf[sizeof(fixture_payload)];
        write_all(cli,fixture_payload,sizeof(fixture_payload)-1);
        CHECK(recv(srv,buf,sizeof(fixture_payload)-1,MSG_WAITALL) == (ssize_t)sizeof(fixture_payload)-1);
        CHECK(memcmp(buf,fixture_payload,sizeof(fixture_payload)-1) == 0);
        write_all(srv,buf,sizeof(fixture_payload)-1);
        CHECK(recv(cli,buf,sizeof(fixture_payload)-1,MSG_WAITALL) == (ssize_t)sizeof(fixture_payload)-1);
        CHECK(memcmp(buf,fixture_payload,sizeof(fixture_payload)-1) == 0); CHECK(close(cli) == 0);
    }
    CHECK(close(srv) == 0);
}
static inline void udp_exchange(void) {
    int srv=socket(AF_INET,SOCK_DGRAM,0),cli=socket(AF_INET,SOCK_DGRAM,0);
    CHECK(srv >= 0 && cli >= 0);
    struct sockaddr_in a=address("198.18.0.1",44445);
    CHECK(bind(srv,(struct sockaddr *)&a,sizeof(a)) == 0);
    CHECK(connect(cli,(struct sockaddr *)&a,sizeof(a)) == 0);
    CHECK(send(cli,fixture_payload,sizeof(fixture_payload)-1,0) == (ssize_t)sizeof(fixture_payload)-1);
    char buf[sizeof(fixture_payload)]; CHECK(recv(srv,buf,sizeof(buf),0) == (ssize_t)sizeof(fixture_payload)-1);
    CHECK(memcmp(buf,fixture_payload,sizeof(fixture_payload)-1) == 0);
    CHECK(close(cli) == 0); CHECK(close(srv) == 0);
}
