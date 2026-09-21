/* Bounded native behaviors for the pinned Falco rule coverage experiment.
 * Must run in a disposable container, never against host files or networks.
 * Setup is a separate process; no detector result is used to decide success. */
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
static const char payload[] = "telemetry-lab-fixture\n";

static void write_all(int fd, const void *buf, size_t size) {
    const char *p = buf;
    while (size) {
        ssize_t n = write(fd, p, size);
        if (n < 0 && errno == EINTR) continue;
        CHECK(n > 0); p += n; size -= (size_t)n;
    }
}
static void file_write(const char *path) {
    int fd = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0600);
    CHECK(fd >= 0); write_all(fd, payload, sizeof(payload)-1); CHECK(close(fd) == 0);
    struct stat st; CHECK(stat(path, &st) == 0 && st.st_size == (off_t)(sizeof(payload)-1));
}
static void file_read(const char *path) {
    char buf[sizeof(payload)];
    int fd = open(path, O_RDONLY); CHECK(fd >= 0);
    ssize_t n = read(fd, buf, sizeof(buf));
    CHECK(n == (ssize_t)(sizeof(payload)-1));
    CHECK(memcmp(buf, payload, sizeof(payload)-1) == 0); CHECK(close(fd) == 0);
}
static void truncate_file(const char *path) {
    int fd = open(path, O_WRONLY | O_TRUNC); CHECK(fd >= 0); CHECK(close(fd) == 0);
    struct stat st; CHECK(stat(path, &st) == 0 && st.st_size == 0);
}
static void directory(const char *path) { CHECK(mkdir(path, 0700) == 0 || errno == EEXIST); }
static void prepare(void) {
    const char *dirs[] = {"/tmp/lab", "/root/.ssh", "/etc/cron.d", "/etc/apt",
        "/etc/apt/sources.list.d", "/boot", NULL};
    for (int i=0; dirs[i]; ++i) directory(dirs[i]);
    const char *files[] = {"/etc/shadow", "/var/log/lab.log", "/root/.bash_history",
        "/root/.ssh/lab_key", "/usr/bin/lab_old", NULL};
    for (int i=0; files[i]; ++i) file_write(files[i]);
}
static void child_ok(pid_t pid) {
    int status; CHECK(waitpid(pid, &status, 0) == pid);
    CHECK(WIFEXITED(status) && WEXITSTATUS(status) == 0);
}
static void copy_helper(int dst) {
    int src = open("/opt/coverage/helper", O_RDONLY); CHECK(src >= 0);
    char buf[16384]; ssize_t n;
    while ((n=read(src, buf, sizeof(buf))) > 0) write_all(dst, buf, (size_t)n);
    CHECK(n == 0); CHECK(close(src) == 0); CHECK(fchmod(dst, 0700) == 0);
}
static void execute_helper(const char *path, int memfd) {
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
static struct sockaddr_in address(const char *ip, unsigned short port) {
    struct sockaddr_in a = {.sin_family=AF_INET, .sin_port=htons(port)};
    CHECK(inet_pton(AF_INET, ip, &a.sin_addr) == 1); return a;
}
static void tcp_exchange(const char *ip, int shell) {
    int lst = socket(AF_INET, SOCK_STREAM, 0); CHECK(lst >= 0);
    struct sockaddr_in a=address(ip, shell ? 4444 : 80);
    CHECK(bind(lst, (struct sockaddr *)&a, sizeof(a)) == 0); CHECK(listen(lst, 1) == 0);
    int srv;
    if (shell) {
        pid_t pid=fork(); CHECK(pid >= 0);
        if (pid == 0) {
            CHECK(close(lst) == 0);
            int cli=socket(AF_INET, SOCK_STREAM, 0); CHECK(cli >= 0);
            CHECK(connect(cli, (struct sockaddr *)&a, sizeof(a)) == 0);
            for (int i=0;i<3;++i) CHECK(dup2(cli,i) >= 0);
            if (cli > 2) close(cli);
            execl("/bin/sh", "sh", (char *)NULL); _exit(127);
        }
        srv=accept(lst, NULL, NULL); CHECK(srv >= 0); CHECK(close(lst) == 0);
        const char command[]="printf 'SHELL_OK\\n'; exit\n";
        write_all(srv,command,sizeof(command)-1);
        char buf[256]={0}; ssize_t used=0,n;
        while (used < (ssize_t)sizeof(buf)-1 && (n=read(srv,buf+used,sizeof(buf)-1-(size_t)used)) > 0) used+=n;
        CHECK(strstr(buf,"SHELL_OK\n") != NULL); child_ok(pid);
    } else {
        int cli=socket(AF_INET, SOCK_STREAM, 0); CHECK(cli >= 0);
        CHECK(connect(cli, (struct sockaddr *)&a, sizeof(a)) == 0);
        srv=accept(lst, NULL, NULL); CHECK(srv >= 0); CHECK(close(lst) == 0);
        char buf[sizeof(payload)];
        write_all(cli,payload,sizeof(payload)-1);
        CHECK(recv(srv,buf,sizeof(payload)-1,MSG_WAITALL) == (ssize_t)sizeof(payload)-1);
        CHECK(memcmp(buf,payload,sizeof(payload)-1) == 0);
        write_all(srv,buf,sizeof(payload)-1);
        CHECK(recv(cli,buf,sizeof(payload)-1,MSG_WAITALL) == (ssize_t)sizeof(payload)-1);
        CHECK(memcmp(buf,payload,sizeof(payload)-1) == 0); CHECK(close(cli) == 0);
    }
    CHECK(close(srv) == 0);
}
static void udp_exchange(void) {
    int srv=socket(AF_INET,SOCK_DGRAM,0),cli=socket(AF_INET,SOCK_DGRAM,0);
    CHECK(srv >= 0 && cli >= 0);
    struct sockaddr_in a=address("198.18.0.1",44445);
    CHECK(bind(srv,(struct sockaddr *)&a,sizeof(a)) == 0);
    CHECK(connect(cli,(struct sockaddr *)&a,sizeof(a)) == 0);
    CHECK(send(cli,payload,sizeof(payload)-1,0) == (ssize_t)sizeof(payload)-1);
    char buf[sizeof(payload)]; CHECK(recv(srv,buf,sizeof(buf),0) == (ssize_t)sizeof(payload)-1);
    CHECK(memcmp(buf,payload,sizeof(payload)-1) == 0);
    CHECK(close(cli) == 0); CHECK(close(srv) == 0);
}
static void trace_child(void) {
    pid_t pid=fork(); CHECK(pid >= 0);
    if (!pid) { for (;;) pause(); }
    CHECK(ptrace(PTRACE_ATTACH,pid,NULL,NULL) == 0);
    int status; CHECK(waitpid(pid,&status,0) == pid && WIFSTOPPED(status));
    CHECK(ptrace(PTRACE_DETACH,pid,NULL,NULL) == 0);
    CHECK(kill(pid,SIGTERM) == 0);
    CHECK(waitpid(pid,&status,0) == pid && WIFSIGNALED(status) && WTERMSIG(status) == SIGTERM);
}
static void run(const char *id) {
    if (!strcmp(id,"negative")) return;
    else if (!strcmp(id,"traversal_read")) file_read("/tmp/lab/../../etc/shadow");
    else if (!strcmp(id,"sensitive_read")) file_read("/etc/shadow");
    else if (!strcmp(id,"log_truncate")) truncate_file("/var/log/lab.log");
    else if (!strcmp(id,"sensitive_symlink")) {
        CHECK(symlink("/etc/shadow","/tmp/lab/link") == 0);
        char buf[64]={0}; CHECK(readlink("/tmp/lab/link",buf,sizeof(buf)-1) == 11);
        CHECK(!strcmp(buf,"/etc/shadow")); CHECK(unlink("/tmp/lab/link") == 0);
    } else if (!strcmp(id,"sensitive_hardlink")) {
        CHECK(link("/etc/shadow","/tmp/lab/hard") == 0);
        struct stat a,b; CHECK(stat("/etc/shadow",&a) == 0 && stat("/tmp/lab/hard",&b) == 0);
        CHECK(a.st_dev == b.st_dev && a.st_ino == b.st_ino); CHECK(unlink("/tmp/lab/hard") == 0);
    } else if (!strcmp(id,"packet_socket")) {
        /* Linux ETH_P_ALL; avoid importing glibc-specific kernel header paths. */
        int fd=socket(AF_PACKET,SOCK_RAW,htons(0x0003)); CHECK(fd >= 0); CHECK(close(fd) == 0);
    } else if (!strcmp(id,"reverse_shell")) tcp_exchange("127.0.0.1",1);
    else if (!strcmp(id,"ptrace_attach")) trace_child();
    else if (!strcmp(id,"ptrace_traceme")) {
        pid_t pid=fork(); CHECK(pid >= 0);
        if (!pid) { CHECK(ptrace(PTRACE_TRACEME,0,NULL,NULL) == 0); _exit(0); }
        child_ok(pid);
    } else if (!strcmp(id,"exec_shm")) execute_helper("/dev/shm/lab-helper",0);
    else if (!strcmp(id,"drop_execute")) execute_helper("/tmp/lab-helper",0);
    else if (!strcmp(id,"memfd_execute")) execute_helper(NULL,1);
    else if (!strcmp(id,"shell_config_write")) file_write("/root/.bashrc");
    else if (!strcmp(id,"cron_write")) file_write("/etc/cron.d/lab_fixture");
    else if (!strcmp(id,"ssh_read")) file_read("/root/.ssh/lab_key");
    else if (!strcmp(id,"udp_exchange")) udp_exchange();
    else if (!strcmp(id,"dev_file")) file_write("/dev/lab_fixture");
    else if (!strcmp(id,"metadata_ec2") || !strcmp(id,"metadata_cloud")) tcp_exchange("169.254.169.254",0);
    else if (!strcmp(id,"history_truncate")) truncate_file("/root/.bash_history");
    else if (!strcmp(id,"setid_mode")) {
        file_write("/tmp/lab/mode"); CHECK(chmod("/tmp/lab/mode",S_ISUID|0600) == 0);
        struct stat st; CHECK(stat("/tmp/lab/mode",&st) == 0 && (st.st_mode&S_ISUID));
    } else if (!strcmp(id,"proc_environ")) {
        int fd=open("/proc/self/environ",O_RDONLY); CHECK(fd >= 0);
        char buf[16384]; ssize_t n=read(fd,buf,sizeof(buf)); CHECK(n > 0);
        const char expected[]="TELEMETRY_LAB_FIXTURE=1";
        CHECK(memmem(buf,(size_t)n,expected,sizeof(expected)-1) != NULL); CHECK(close(fd) == 0);
    } else if (!strcmp(id,"authorized_keys")) file_write("/root/.ssh/authorized_keys");
    else if (!strcmp(id,"repository_write")) file_write("/etc/apt/sources.list.d/lab.list");
    else if (!strcmp(id,"binary_write")) file_write("/usr/bin/lab_fixture");
    else if (!strcmp(id,"monitored_write")) file_write("/boot/lab_fixture");
    else if (!strcmp(id,"etc_write")) file_write("/etc/lab_fixture");
    else if (!strcmp(id,"root_write")) file_write("/root/lab_fixture");
    else if (!strcmp(id,"binary_rename")) {
        CHECK(rename("/usr/bin/lab_old","/usr/bin/lab_new") == 0);
        CHECK(access("/usr/bin/lab_old",F_OK) == -1 && errno == ENOENT); file_read("/usr/bin/lab_new");
    } else if (!strcmp(id,"binary_mkdir")) {
        CHECK(mkdir("/usr/bin/lab_directory",0700) == 0);
        struct stat st; CHECK(stat("/usr/bin/lab_directory",&st) == 0 && S_ISDIR(st.st_mode));
        CHECK(rmdir("/usr/bin/lab_directory") == 0);
    } else { fprintf(stderr,"Unknown case: %s\n",id); exit(2); }
}
int main(int argc, char **argv) {
    CHECK(access("/.dockerenv",F_OK) == 0);
    const char *flag=getenv("TELEMETRY_LAB_FIXTURE"); CHECK(flag && !strcmp(flag,"1"));
    CHECK(argc == 2); alarm(10);
    if (!strcmp(argv[1],"--prepare")) { prepare(); return 0; }
    run(argv[1]); printf("CASE_OK %s\n",argv[1]); return 0;
}
