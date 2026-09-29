#pragma once
/* Fixed external utilities: only their launch path varies by measured language. */
static inline void launch_checked(const char *const *args,const char *expected,const char *envkey,const char *envval) {
    int p[2]; CHECK(pipe(p)==0); pid_t pid=fork(); CHECK(pid>=0);
    if(pid==0) { CHECK(close(p[0])==0); CHECK(dup2(p[1],STDOUT_FILENO)>=0); CHECK(close(p[1])==0);
        if(envkey) CHECK(setenv(envkey,envval,1)==0);
        execv(args[0],(char *const *)args); _exit(127); }
    CHECK(close(p[1])==0); char data[1024]; size_t total=0; ssize_t n;
    while((n=read(p[0],data+total,sizeof(data)-total))>0) {total+=(size_t)n; CHECK(total<sizeof(data));}
    CHECK(n==0); CHECK(close(p[0])==0); child_ok(pid);
    CHECK(total==strlen(expected) && memcmp(data,expected,total)==0);
}
