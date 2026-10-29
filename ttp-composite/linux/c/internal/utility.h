#pragma once
/* Common assertions and process plumbing; no case selector or behavior dispatcher. */
static inline void verify_bytes(const char *path, const char *expected, size_t size) {
    FILE *f=fopen(path,"rb"); CHECK(f); char data[4096]; size_t n=fread(data,1,sizeof(data),f);
    CHECK(!ferror(f)); CHECK(fclose(f)==0); CHECK(n==size && memcmp(data,expected,size)==0);
}
static inline void launch_verified(const char *const *args,const char *expected,int prefix,const char *envkey,const char *envval) {
    int p[2]; CHECK(pipe(p)==0); pid_t pid=fork(); CHECK(pid>=0);
    if(pid==0) { CHECK(close(p[0])==0); CHECK(dup2(p[1],STDOUT_FILENO)>=0); CHECK(close(p[1])==0);
        if(envkey) CHECK(setenv(envkey,envval,1)==0);
        execv(args[0],(char *const *)args); _exit(127); }
    CHECK(close(p[1])==0); char data[4096]; size_t total=0; ssize_t n;
    while((n=read(p[0],data+total,sizeof(data)-total))>0) {total+=(size_t)n; CHECK(total<sizeof(data));}
    CHECK(n==0); CHECK(close(p[0])==0); child_ok(pid);
    CHECK((prefix ? total>=strlen(expected) : total==strlen(expected)) && memcmp(data,expected,strlen(expected))==0);
}
static inline void port_exchange(unsigned short port) {
    int lst=socket(AF_INET,SOCK_STREAM,0); CHECK(lst>=0);
    struct sockaddr_in a; memset(&a,0,sizeof(a)); a.sin_family=AF_INET; a.sin_port=htons(port);
    CHECK(inet_pton(AF_INET,"198.18.0.1",&a.sin_addr)==1);
    CHECK(bind(lst,(struct sockaddr *)&a,sizeof(a))==0); CHECK(listen(lst,1)==0);
    int cli=socket(AF_INET,SOCK_STREAM,0); CHECK(cli>=0);
    CHECK(connect(cli,(struct sockaddr *)&a,sizeof(a))==0);
    int srv=accept(lst,NULL,NULL); CHECK(srv>=0); CHECK(close(lst)==0);
    char buf[sizeof(fixture_payload)]; write_all(cli,fixture_payload,sizeof(fixture_payload)-1);
    CHECK(recv(srv,buf,sizeof(fixture_payload)-1,MSG_WAITALL)==(ssize_t)sizeof(fixture_payload)-1);
    CHECK(memcmp(buf,fixture_payload,sizeof(fixture_payload)-1)==0);
    write_all(srv,buf,sizeof(fixture_payload)-1);
    CHECK(recv(cli,buf,sizeof(fixture_payload)-1,MSG_WAITALL)==(ssize_t)sizeof(fixture_payload)-1);
    CHECK(memcmp(buf,fixture_payload,sizeof(fixture_payload)-1)==0);
    CHECK(close(cli)==0); CHECK(close(srv)==0);
}
