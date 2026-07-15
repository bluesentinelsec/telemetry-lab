/* Wire format shared verbatim between the BPF program (kernel, C) and the
 * user-space engine (C++). This is the on-the-ring-buffer layout; it is a plain
 * C POD so both sides agree on it byte-for-byte.
 *
 * A syscall is reported as two records: a SYS_ENTER (carrying the raw args and
 * any decoded pointer arguments) and a SYS_EXIT (carrying the return value). The
 * engine pairs them per-thread into a single domain event with args, result,
 * and duration. fork/exec/exit bound the process tree.
 *
 * Keep this header valid in both a BPF C target and a hosted C++ TU: no libc
 * includes, no C++ constructs.
 */
#ifndef TMON_BPF_EVENT_H
#define TMON_BPF_EVENT_H

#define TMON_COMM_LEN 16
#define TMON_SYSCALL_ARGS 6
#define TMON_STR_LEN 256 /* decoded path buffer */
#define TMON_SADDR_LEN 28 /* raw sockaddr bytes (fits sockaddr_in6) */

enum tmon_kind {
	TMON_SYS_ENTER = 0,
	TMON_SYS_EXIT = 1,
	TMON_FORK = 2,
	TMON_EXEC = 3,
	TMON_EXIT = 4,
};

struct tmon_event {
	unsigned long long ts_ns; /* boot-time nanoseconds */
	unsigned int kind;        /* enum tmon_kind */
	unsigned int pid;         /* tgid */
	unsigned int tid;         /* thread id */
	unsigned int child_pid;   /* TMON_FORK: tgid of the new child */
	long long syscall_nr;     /* SYS_ENTER/SYS_EXIT: syscall number, else -1 */
	long long ret;            /* SYS_EXIT: return value */
	int exit_code;            /* TMON_EXIT: process exit code */
	unsigned int str_len;     /* SYS_ENTER: bytes in str (incl NUL), 0 if none */
	unsigned int saddr_len;   /* SYS_ENTER: bytes in saddr, 0 if none */
	int str_argno;            /* SYS_ENTER: arg index the path came from, else -1 */
	int saddr_argno;          /* SYS_ENTER: arg index the sockaddr came from, else -1 */
	unsigned long long args[TMON_SYSCALL_ARGS]; /* SYS_ENTER: raw scalar args */
	char comm[TMON_COMM_LEN];                   /* acting task command name */
	unsigned char saddr[TMON_SADDR_LEN];        /* decoded: raw sockaddr */
	/* `str` MUST be the last member: records are emitted variable-length as
	 * offsetof(str) + str_len, so only the bytes of the decoded path actually
	 * present travel on the ring buffer (most events carry none). */
	char str[TMON_STR_LEN];                     /* decoded: path / exec filename */
};

#endif /* TMON_BPF_EVENT_H */
