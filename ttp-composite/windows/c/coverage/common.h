#pragma once
#define WIN32_LEAN_AND_MEAN
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define ROOT "C:\\lab\\windows-coverage"
#define CHECK(x) do { if (!(x)) { fprintf(stderr,"FAIL line=%d expression=%s winerror=%lu errno=%d\n",__LINE__,#x,(unsigned long)GetLastError(),errno); exit(1); } } while (0)
#include <errno.h>
/* Every executable has exactly one behavior. --control skips that behavior. */
static inline int fixture_begin(int argc, char **argv, const char *id) {
    const char *flag = getenv("TELEMETRY_LAB_FIXTURE");
    CHECK(flag && !strcmp(flag,"1"));
    CHECK(argc == 1 || (argc == 2 && !strcmp(argv[1],"--control")));
    if (argc == 2) { printf("CONTROL_OK %s\n", id); return 0; }
    return 1;
}
static inline void success(const char *id) { printf("BEHAVIOR_OK %s\n",id); }
static inline void file_equal(const char *a, const char *b) {
    FILE *fa=fopen(a,"rb"), *fb=fopen(b,"rb"); CHECK(fa && fb);
    unsigned char ba[4096],bb[4096]; size_t na,nb;
    do { na=fread(ba,1,sizeof ba,fa); nb=fread(bb,1,sizeof bb,fb);
         CHECK(na==nb && !memcmp(ba,bb,na)); } while(na);
    CHECK(!ferror(fa) && !ferror(fb)); CHECK(fclose(fa)==0 && fclose(fb)==0);
}
static inline void copy_verified(const char *src, const char *dst) {
    FILE *in=fopen(src,"rb"),*out=fopen(dst,"wb"); CHECK(in && out);
    char bytes[4096]; size_t n;
    while((n=fread(bytes,1,sizeof bytes,in))!=0) CHECK(fwrite(bytes,1,n,out)==n);
    CHECK(!ferror(in)); CHECK(fflush(out)==0); CHECK(fclose(out)==0); CHECK(fclose(in)==0);
    file_equal(src,dst);
}
static inline void appdata_path(char *out,size_t size,const char *suffix) {
    const char *app=getenv("APPDATA"); CHECK(app && *app);
    int n=snprintf(out,size,"%s\\%s",app,suffix); CHECK(n>0 && (size_t)n<size);
}
static inline void set_registry_verified(const char *path,const char *name,const char *value) {
    HKEY key; CHECK(RegOpenKeyExA(HKEY_CURRENT_USER,path,0,KEY_SET_VALUE|KEY_QUERY_VALUE,&key)==ERROR_SUCCESS);
    DWORD size=(DWORD)strlen(value)+1;
    CHECK(RegSetValueExA(key,name,0,REG_SZ,(const BYTE*)value,size)==ERROR_SUCCESS);
    BYTE actual[1024]; DWORD type=0,n=sizeof actual;
    CHECK(RegQueryValueExA(key,name,NULL,&type,actual,&n)==ERROR_SUCCESS);
    CHECK(type==REG_SZ && n==size && !memcmp(actual,value,size));
    CHECK(RegCloseKey(key)==ERROR_SUCCESS);
}
static inline void socket_start(void) { WSADATA w; CHECK(WSAStartup(MAKEWORD(2,2),&w)==0); }
static inline SOCKET connect_local(unsigned short port) {
    SOCKET s=socket(AF_INET,SOCK_STREAM,IPPROTO_TCP); CHECK(s!=INVALID_SOCKET);
    DWORD timeout=5000;
    CHECK(setsockopt(s,SOL_SOCKET,SO_RCVTIMEO,(const char*)&timeout,sizeof timeout)==0);
    CHECK(setsockopt(s,SOL_SOCKET,SO_SNDTIMEO,(const char*)&timeout,sizeof timeout)==0);
    struct sockaddr_in addr; memset(&addr,0,sizeof addr); addr.sin_family=AF_INET;
    addr.sin_port=htons(port); addr.sin_addr.s_addr=htonl(INADDR_LOOPBACK);
    CHECK(connect(s,(struct sockaddr*)&addr,sizeof addr)==0); return s;
}
static inline void socket_send_all(SOCKET s,const char *buf,int n) {
    while(n) { int k=send(s,buf,n,0); CHECK(k>0); buf+=k; n-=k; }
}
static inline void socket_recv_all(SOCKET s,char *buf,int n) {
    while(n) { int k=recv(s,buf,n,0); CHECK(k>0); buf+=k; n-=k; }
}
static inline void tcp_exchange(unsigned short port) {
    const char marker[]="telemetry-lab\n"; char reply[sizeof marker];
    socket_start(); SOCKET s=connect_local(port);
    socket_send_all(s,marker,sizeof marker-1); socket_recv_all(s,reply,sizeof marker-1);
    CHECK(!memcmp(marker,reply,sizeof marker-1)); CHECK(closesocket(s)==0); CHECK(WSACleanup()==0);
}
static inline void resolve_verified(const char *name) {
    socket_start(); struct addrinfo hints; memset(&hints,0,sizeof hints);
    hints.ai_family=AF_INET; hints.ai_socktype=SOCK_STREAM;
    struct addrinfo *answers=NULL; int rc=getaddrinfo(name,NULL,&hints,&answers);
    CHECK(rc==0 && answers!=NULL);
    /* Fixed isolated fixture answer, not an external service. */
    for(struct addrinfo *a=answers;a;a=a->ai_next) {
        CHECK(a->ai_family==AF_INET);
        CHECK(((struct sockaddr_in*)a->ai_addr)->sin_addr.s_addr==htonl(0x7f00002a));
    }
    freeaddrinfo(answers); CHECK(WSACleanup()==0);
}
