// A tiny, self-contained workload for demonstrating tmon. It deliberately
// exercises the four things a telemetry study cares about: file I/O, network
// I/O (including a failing call), and spawning a subprocess. Trace it with:
//
//   cc -O2 -o specimen examples/specimen.c
//   sudo tmon -- ./specimen
//   sudo tmon --format json -o specimen.jsonl -- ./specimen
#define _GNU_SOURCE
#include <arpa/inet.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/wait.h>
#include <unistd.h>

int main(void) {
  // 1. Write a file, then read it back.
  const char *path = "/tmp/tmon-specimen.dat";
  int fd = open(path, O_CREAT | O_WRONLY | O_TRUNC, 0644);
  if (fd >= 0) {
    write(fd, "telemetry-lab\n", 14);
    close(fd);
  }
  fd = open(path, O_RDONLY);
  if (fd >= 0) {
    char buf[64];
    ssize_t n = read(fd, buf, sizeof buf);
    (void)n;
    close(fd);
  }

  // 2. Open a TCP socket and connect to a closed port -- a deliberate failure,
  //    so the trace shows a non-zero errno (ECONNREFUSED).
  int s = socket(AF_INET, SOCK_STREAM, 0);
  if (s >= 0) {
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof addr);
    addr.sin_family = AF_INET;
    addr.sin_port = htons(9999);
    inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);
    connect(s, (struct sockaddr *)&addr, sizeof addr);
    close(s);
  }

  // 3. Spawn a subprocess (fork + execve), so the trace crosses the tree.
  pid_t pid = fork();
  if (pid == 0) {
    execl("/bin/echo", "echo", "hello-from-child", (char *)0);
    _exit(127);
  } else if (pid > 0) {
    int status;
    waitpid(pid, &status, 0);
  }
  return 0;
}
