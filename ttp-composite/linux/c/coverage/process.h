#pragma once
#include "common.h"
static inline void copy_helper(int dst) {
    int src = open("/opt/coverage/helper", O_RDONLY); CHECK(src >= 0);
    char buf[16384]; ssize_t n;
    while ((n=read(src, buf, sizeof(buf))) > 0) write_all(dst, buf, (size_t)n);
    CHECK(n == 0); CHECK(close(src) == 0); CHECK(fchmod(dst, 0700) == 0);
}
static inline void execute_helper(const char *path, int memfd) {
    int fd = memfd ? (int)syscall(SYS_memfd_create, "lab-helper", 0) :
        open(path, O_WRONLY | O_CREAT | O_TRUNC, 0700);
    CHECK(fd >= 0); copy_helper(fd);
    if (!memfd) CHECK(close(fd) == 0);
    int pipefd[2]; CHECK(pipe(pipefd) == 0);
    pid_t pid = fork(); CHECK(pid >= 0);
    if (pid == 0) {
        close(pipefd[0]); CHECK(dup2(pipefd[1], STDOUT_FILENO) >= 0); close(pipefd[1]);
        char *args[] = {memfd ? "lab-helper" : (char *)path, NULL};
        if (memfd) fexecve(fd, args, environ); else execve(path, args, environ);
        _exit(127);
    }
    CHECK(close(pipefd[1]) == 0);
    char buf[64] = {0}; ssize_t n = read(pipefd[0], buf, sizeof(buf)-1);
    CHECK(n > 0 && strstr(buf, "HELPER_OK\n") != NULL);
    CHECK(close(pipefd[0]) == 0); child_ok(pid);
    if (memfd) CHECK(close(fd) == 0); else CHECK(unlink(path) == 0);
}
static inline void trace_child(void) {
    pid_t pid=fork(); CHECK(pid >= 0);
    if (!pid) { for (;;) pause(); }
    CHECK(ptrace(PTRACE_ATTACH,pid,NULL,NULL) == 0);
    int status; CHECK(waitpid(pid,&status,0) == pid && WIFSTOPPED(status));
    CHECK(ptrace(PTRACE_DETACH,pid,NULL,NULL) == 0);
    CHECK(kill(pid,SIGTERM) == 0);
    CHECK(waitpid(pid,&status,0) == pid && WIFSIGNALED(status) && WTERMSIG(status) == SIGTERM);
}
