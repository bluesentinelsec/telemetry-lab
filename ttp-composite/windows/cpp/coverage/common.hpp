#pragma once
#define WIN32_LEAN_AND_MEAN
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include <stdio.h>
#include <cstdlib>
#include <cstring>
#include <string.h>
#include <stdint.h>
#include <array>
#include <fstream>
#include <iostream>
#include <string>

#define ROOT "C:\\lab\\windows-coverage"
#define CHECK(x) do { if (!(x)) { std::cerr << "FAIL line=" << __LINE__ << " expression=" << #x << " winerror=" << GetLastError() << " errno=" << errno << "\n"; std::exit(1); } } while (0)
#include <errno.h>
/* Every executable has exactly one behavior. --control skips that behavior. */
static inline int fixture_begin(int argc, char **argv, const char *id) {
    const char *flag = getenv("TELEMETRY_LAB_FIXTURE");
    CHECK(flag && std::string(flag)=="1");
    CHECK(argc == 1 || (argc == 2 && std::string(argv[1])=="--control"));
    if (argc == 2) { std::cout << "CONTROL_OK " << id << "\n"; return 0; }
    return 1;
}
static inline void success(const char *id) { std::cout << "BEHAVIOR_OK " << id << "\n"; }
// Use the selected C++ library for binary file I/O; paths and fixture bytes
// match C. Flush, close and read back independently of any detection outcome.
static inline void file_equal(const char *a, const char *b) {
    std::ifstream fa(a,std::ios::binary),fb(b,std::ios::binary); CHECK(fa.is_open() && fb.is_open());
    std::array<char,4096> ba{},bb{};
    for (;;) {
        fa.read(ba.data(),ba.size());fb.read(bb.data(),bb.size());
        CHECK(!fa.bad() && !fb.bad());
        CHECK(fa.gcount()==fb.gcount());
        CHECK(!std::memcmp(ba.data(),bb.data(),static_cast<size_t>(fa.gcount())));
        if(fa.gcount()==0) {CHECK(fa.eof() && fb.eof());break;}
    }
}
static inline void copy_verified(const char *src,const char *dst) {
    std::ifstream in(src,std::ios::binary);
    std::ofstream out(dst,std::ios::binary|std::ios::trunc); CHECK(in.is_open() && out.is_open());
    std::array<char,4096> bytes{};
    for (;;) {
        in.read(bytes.data(),bytes.size());CHECK(!in.bad());
        auto n=in.gcount();if(!n){CHECK(in.eof());break;}
        out.write(bytes.data(),n);CHECK(out.good());
    }
    out.flush();CHECK(out.good());out.close();CHECK(!out.fail());
    // Clear the expected EOF state before checking close.
    in.clear();in.close();CHECK(!in.fail());file_equal(src,dst);
}
static inline void appdata_path(char *out,size_t size,const char *suffix) {
    const char *app=std::getenv("APPDATA");CHECK(app && *app);
    const std::string path=std::string(app)+"\\"+suffix;
    CHECK(path.size()<size);std::memcpy(out,path.c_str(),path.size()+1);
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
