#include "../common.hpp"
#include <sched.h>

int main(int argc,char **argv) {
    if (!fixture_begin(argc,argv,"namespace_unshare_denied")) return 0;
    struct stat before, after; CHECK(stat("/proc/thread-self/ns/net",&before)==0);
    errno=0; CHECK(unshare(CLONE_NEWNET)==-1 && errno==EPERM); CHECK(stat("/proc/thread-self/ns/net",&after)==0 && before.st_ino==after.st_ino);
    std::cout << "CASE_OK namespace_unshare_denied\n";
    return 0;
}
