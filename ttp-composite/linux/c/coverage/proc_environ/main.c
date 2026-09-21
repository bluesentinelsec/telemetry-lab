#include "../common.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"proc_environ")) return 0;
    int fd=open("/proc/self/environ",O_RDONLY); CHECK(fd >= 0);
    char buf[16384]; ssize_t n=read(fd,buf,sizeof(buf)); CHECK(n > 0);
    const char expected[]="TELEMETRY_LAB_FIXTURE=1";
    CHECK(memmem(buf,(size_t)n,expected,sizeof(expected)-1) != NULL); CHECK(close(fd) == 0);
    printf("CASE_OK proc_environ\n");
    return 0;
}
