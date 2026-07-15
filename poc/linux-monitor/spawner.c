// PoC test subject: a process that spawns a child, to exercise descendant
// tracking. The monitor should capture this process's syscalls AND the child's
// (via exec of `id`), plus a FORK event -- and nothing from unrelated processes.

#include <unistd.h>
#include <sys/wait.h>

int main(void)
{
    getpid();               // a syscall from the parent
    pid_t c = fork();
    if (c == 0) {
        execlp("id", "id", (char *)0);   // descendant makes its own syscalls
        _exit(1);
    }
    waitpid(c, 0, 0);
    write(1, "spawner done\n", 13);
    return 0;
}
