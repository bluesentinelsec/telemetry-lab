#include "common.h"
/* Harness fixture, never a measured composite. One server process per fixed port. */
int main(int argc,char **argv) {
    CHECK(argc==2); char *end; long port=strtol(argv[1],&end,10); CHECK(!*end && port>0 && port<65536);
    socket_start(); SOCKET server=socket(AF_INET,SOCK_STREAM,IPPROTO_TCP); CHECK(server!=INVALID_SOCKET);
    BOOL exclusive=TRUE; CHECK(setsockopt(server,SOL_SOCKET,SO_EXCLUSIVEADDRUSE,(char*)&exclusive,sizeof exclusive)==0);
    struct sockaddr_in addr; memset(&addr,0,sizeof addr); addr.sin_family=AF_INET; addr.sin_port=htons((unsigned short)port);addr.sin_addr.s_addr=htonl(INADDR_LOOPBACK);
    CHECK(bind(server,(struct sockaddr*)&addr,sizeof addr)==0); CHECK(listen(server,8)==0);
    puts("LISTENER_READY"); fflush(stdout);
    for(;;) { SOCKET client=accept(server,NULL,NULL); CHECK(client!=INVALID_SOCKET);
        DWORD timeout=5000; CHECK(setsockopt(client,SOL_SOCKET,SO_RCVTIMEO,(char*)&timeout,sizeof timeout)==0);
        char buf[128]; int count=0,n;
        while((n=recv(client,buf,sizeof buf,0))>0) {socket_send_all(client,buf,n);count+=n;}
        printf("EXCHANGE bytes=%d\n",count);fflush(stdout);closesocket(client);
    }
}
