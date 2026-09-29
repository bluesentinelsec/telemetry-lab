#include "../common.hpp"
#include <sched.h>

int main(int argc,char **argv) {
    if (!fixture_begin(argc,argv,"namespace_unshare")) return 0;
    struct stat before, after; CHECK(stat("/proc/thread-self/ns/user",&before)==0);
    CHECK(unshare(CLONE_NEWUSER)==0); CHECK(stat("/proc/thread-self/ns/user",&after)==0 && before.st_ino!=after.st_ino);
    std::cout << "CASE_OK namespace_unshare\n";
    return 0;
}
