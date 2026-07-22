//! ptrace_antidebug composite (ATT&CK T1622) -- PTRACE_TRACEME anti-debug.
//!
//! A robustness control (effect-keyed, expected to FIRE on every substrate; the
//! PoC confirmed this one robust). Falco's "PTRACE anti-debug attempt" keys on a
//! ptrace(PTRACE_TRACEME) call, a classic self-debugging / anti-analysis trick.
//! Benign: it makes the single ptrace call and exits. Detonates in a container.
//!
//! std has no ptrace binding and this study forbids third-party crates (no
//! libc), so the single ptrace(PTRACE_TRACEME, 0, 0, 0) is issued as a raw Linux
//! syscall via inline asm -- exactly the one call the C reference makes. The
//! syscall number and calling convention are arch-specific, so the asm is gated
//! on target_arch (x86_64 + aarch64, the two lab/build substrates).

// PTRACE_TRACEME request == 0 on Linux, all architectures.

#[cfg(target_arch = "x86_64")]
fn ptrace_traceme() {
    // SYS_ptrace = 101 on x86_64. Syscall ABI: nr in rax, args in
    // rdi/rsi/rdx/r10; the `syscall` instruction clobbers rcx and r11.
    unsafe {
        let ret: i64;
        core::arch::asm!(
            "syscall",
            in("rax") 101i64, // SYS_ptrace
            in("rdi") 0i64,   // PTRACE_TRACEME
            in("rsi") 0i64,   // pid (ignored)
            in("rdx") 0i64,   // addr (ignored)
            in("r10") 0i64,   // data (ignored)
            lateout("rax") ret,
            out("rcx") _,
            out("r11") _,
        );
        let _ = ret;
    }
}

#[cfg(target_arch = "aarch64")]
fn ptrace_traceme() {
    // SYS_ptrace = 117 on aarch64. Syscall ABI: nr in x8, args in x0-x3; the
    // `svc #0` instruction traps into the kernel and returns in x0.
    unsafe {
        let ret: i64;
        core::arch::asm!(
            "svc #0",
            in("x8") 117i64,   // SYS_ptrace
            in("x0") 0i64,     // PTRACE_TRACEME
            in("x1") 0i64,     // pid (ignored)
            in("x2") 0i64,     // addr (ignored)
            in("x3") 0i64,     // data (ignored)
            lateout("x0") ret,
        );
        let _ = ret;
    }
}

#[cfg(not(any(target_arch = "x86_64", target_arch = "aarch64")))]
compile_error!("ptrace_antidebug: raw ptrace syscall only wired for x86_64 and aarch64");

fn main() {
    // The single fired syscall: ptrace(PTRACE_TRACEME, 0, 0, 0).
    ptrace_traceme();
}
