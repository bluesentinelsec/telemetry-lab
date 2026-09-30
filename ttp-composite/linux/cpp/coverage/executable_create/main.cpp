#include "../common.hpp"
#include "../utility.h"
int main(int argc,char **argv) {
if (!fixture_begin(argc,argv,"executable_create")) return 0;
umask(0); int fd=open("/tmp/lab/executable-new",O_WRONLY|O_CREAT|O_EXCL,0700); CHECK(fd>=0); CHECK(close(fd)==0); struct stat st; CHECK(stat("/tmp/lab/executable-new",&st)==0); CHECK((st.st_mode&0777)==0700);
std::cout << "CASE_OK executable_create\n";
}
