#include "../common.h"
#include "../utility.h"
int main(int argc,char **argv) {
if (!fixture_begin(argc,argv,"hidden_file")) return 0;
int fd=open("/tmp/lab/.hidden-fixture",O_WRONLY|O_CREAT|O_EXCL,0600); CHECK(fd>=0); write_all(fd,fixture_payload,sizeof(fixture_payload)-1); CHECK(close(fd)==0); verify_bytes("/tmp/lab/.hidden-fixture",fixture_payload,sizeof(fixture_payload)-1);
printf("CASE_OK hidden_file\n");
}
