#include "../common.hpp"

int main(int argc,char **argv) {
    if (!fixture_begin(argc,argv,"userfaultfd_create")) return 0;
    CHECK(setgid(65534)==0 && setuid(65534)==0); CHECK(getuid()==65534);
    int fd=(int)syscall(SYS_userfaultfd,O_CLOEXEC|O_NONBLOCK|1); CHECK(fd>=0); CHECK(close(fd)==0);
    std::cout << "CASE_OK userfaultfd_create\n";
    return 0;
}
