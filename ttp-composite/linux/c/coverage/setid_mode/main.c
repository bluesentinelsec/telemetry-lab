#include "../file_io.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"setid_mode")) return 0;
    file_write("/tmp/lab/mode"); CHECK(chmod("/tmp/lab/mode",S_ISUID|0600) == 0);
    struct stat st; CHECK(stat("/tmp/lab/mode",&st) == 0 && (st.st_mode&S_ISUID));
    printf("CASE_OK setid_mode\n");
    return 0;
}
