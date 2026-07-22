// ptrace_antidebug composite (ATT&CK T1622) -- PTRACE_TRACEME anti-debug.
//
// Robustness control (expected to FIRE on every substrate; PoC-confirmed robust):
// Falco's "PTRACE anti-debug attempt" keys on ptrace(PTRACE_TRACEME). Issued as a
// raw syscall to avoid a third-party dependency (PTRACE_TRACEME == 0). Benign.
package main

import "syscall"

const ptraceTraceme = 0

func main() {
	syscall.Syscall(syscall.SYS_PTRACE, ptraceTraceme, 0, 0)
}
