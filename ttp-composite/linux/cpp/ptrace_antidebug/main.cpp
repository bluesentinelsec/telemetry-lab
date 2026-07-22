// ptrace_antidebug composite (ATT&CK T1622) -- PTRACE_TRACEME anti-debug.
//
// A robustness control (effect-keyed, expected to FIRE on every substrate; the
// PoC confirmed this one robust). Falco's "PTRACE anti-debug attempt" keys on a
// ptrace(PTRACE_TRACEME) call, a classic self-debugging / anti-analysis trick.
// Benign: it makes the single ptrace call and exits. Detonates in a container.
#include <sys/ptrace.h>

int main() {
    ptrace(PTRACE_TRACEME, 0, 0, 0);
    return 0;
}
