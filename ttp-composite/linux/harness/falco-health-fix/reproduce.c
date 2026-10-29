#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <string.h>
/* Diagnostic only: compare the same open syscall with a cold/warm pathname
 * mapping. The fixture file contains a NUL-terminated /etc/shadow pathname. */
int main(int argc, char **argv) {
    int fixture = open("/tmp/falco-health-path", O_RDONLY);
    if (fixture < 0) { perror("fixture"); return 1; }
    char *path = mmap(NULL, 4096, PROT_READ, MAP_PRIVATE, fixture, 0);
    if (path == MAP_FAILED) { perror("mmap"); return 1; }
    close(fixture);
    if (argc > 1 && strcmp(argv[1], "warm") == 0) {
        volatile char first = path[0]; (void)first;
    }
    long fd = syscall(SYS_open, path, O_RDONLY, 0);
    if (fd < 0) { perror("target open"); return 1; }
    close((int)fd);
    munmap(path, 4096);
    return 0;
}
