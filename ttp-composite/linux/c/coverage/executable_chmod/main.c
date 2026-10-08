#include "../common.h"
#include "../utility.h"
int main(int argc,char **argv) {
if (!fixture_begin(argc,argv,"executable_chmod")) return 0;
CHECK(chmod("/tmp/lab/executable-mode",0700)==0); struct stat st; CHECK(stat("/tmp/lab/executable-mode",&st)==0); CHECK((st.st_mode&0777)==0700);
printf("CASE_OK executable_chmod\n");
}
