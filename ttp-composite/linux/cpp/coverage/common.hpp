#pragma once
#include <iostream>
#include <string>
#include <filesystem>
#include <fstream>
#include <iterator>
namespace fs = std::filesystem;
#include <arpa/inet.h>
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ptrace.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

extern char **environ;
#define CHECK(x) do { if (!(x)) { fprintf(stderr, "FAIL line %d: %s: %s\n", __LINE__, #x, strerror(errno)); exit(1); } } while (0)
#define fixture_payload "telemetry-lab-fixture\n"

static inline void write_all(int fd, const void *buf, size_t size) {
    const char *p = static_cast<const char *>(buf);
    while (size) {
        ssize_t n = write(fd, p, size);
        if (n < 0 && errno == EINTR) continue;
        CHECK(n > 0); p += n; size -= (size_t)n;
    }
}
static inline void child_ok(pid_t pid) {
    int status; CHECK(waitpid(pid, &status, 0) == pid);
    CHECK(WIFEXITED(status) && WEXITSTATUS(status) == 0);
}

/* A control starts the exact same binary but omits its sole tested behavior. */
static inline int fixture_begin(int argc, char **argv, const char *id) {
    CHECK(access("/.dockerenv", F_OK) == 0);
    const char *flag=getenv("TELEMETRY_LAB_FIXTURE");
    CHECK(flag && !strcmp(flag,"1"));
    CHECK(argc == 1 || (argc == 2 && !strcmp(argv[1],"--control")));
    alarm(10);
    // Match the C fixture permissions for standard-library file/directory creation.
    umask(0077);
    if (argc == 2) { std::cout << "CONTROL_OK " << id << "\n"; return 0; }
    return 1;
}
