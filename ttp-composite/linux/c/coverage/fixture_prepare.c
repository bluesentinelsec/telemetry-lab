#include "file_io.h"
static void prepare(void) {
    const char *dirs[] = {"/tmp/lab", "/root/.ssh", "/etc/cron.d", "/etc/apt",
        "/etc/apt/sources.list.d", "/boot", NULL};
    for (int i=0; dirs[i]; ++i) directory(dirs[i]);
    const char *files[] = {"/etc/shadow", "/var/log/lab.log", "/root/.bash_history",
        "/root/.ssh/lab_key", "/usr/bin/lab_old", NULL};
    for (int i=0; files[i]; ++i) file_write(files[i]);
}
int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"fixture_prepare")) return 0;
    prepare(); return 0;
}
