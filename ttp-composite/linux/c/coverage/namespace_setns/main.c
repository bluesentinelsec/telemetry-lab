#include "../common.h"
#include <sched.h>

int main(int argc,char **argv) {
    if (!fixture_begin(argc,argv,"namespace_setns")) return 0;
    struct stat before, after, target; CHECK(stat("/proc/thread-self/ns/net",&before)==0);
    int fd=open("/tmp/lab/netns",O_RDONLY); CHECK(fd>=0 && fstat(fd,&target)==0);
    CHECK(before.st_ino!=target.st_ino); CHECK(setns(fd,CLONE_NEWNET)==0);
    CHECK(stat("/proc/thread-self/ns/net",&after)==0 && after.st_ino==target.st_ino); CHECK(close(fd)==0);
    printf("CASE_OK namespace_setns\n");
    return 0;
}
