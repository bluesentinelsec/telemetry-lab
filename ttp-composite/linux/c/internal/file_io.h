#pragma once
#include "common.h"
static inline void file_write(const char *path) {
    int fd = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0600);
    CHECK(fd >= 0); write_all(fd, fixture_payload, sizeof(fixture_payload)-1); CHECK(close(fd) == 0);
    struct stat st; CHECK(stat(path, &st) == 0 && st.st_size == (off_t)(sizeof(fixture_payload)-1));
}
static inline void file_read(const char *path) {
    char buf[sizeof(fixture_payload)];
    int fd = open(path, O_RDONLY); CHECK(fd >= 0);
    ssize_t n = read(fd, buf, sizeof(buf));
    CHECK(n == (ssize_t)(sizeof(fixture_payload)-1));
    CHECK(memcmp(buf, fixture_payload, sizeof(fixture_payload)-1) == 0); CHECK(close(fd) == 0);
}
static inline void truncate_file(const char *path) {
    int fd = open(path, O_WRONLY | O_TRUNC); CHECK(fd >= 0); CHECK(close(fd) == 0);
    struct stat st; CHECK(stat(path, &st) == 0 && st.st_size == 0);
}
static inline void directory(const char *path) { CHECK(mkdir(path, 0700) == 0 || errno == EEXIST); }
