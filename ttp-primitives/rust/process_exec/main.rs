//! process_exec primitive: replace the current process image with a no-op.
//!
//! Distinct from `spawn` (which forks a child and reaps it): exec-family calls
//! REPLACE the calling image in place, so no new pid is created and control
//! never returns on success. This exercises the execve telemetry path without
//! the fork/clone that spawn emits -- a different process-lifecycle signal.
//!
//! `CommandExt::exec` searches PATH for `true`, whose only job is to exit 0;
//! since exec replaces this image, that exit status becomes the primitive's.
//! `exec` returns only if the exec itself failed, in which case we exit 1.
//!
//! Linux-only: Windows has no true exec-replace semantic (see issue #44).

use std::os::unix::process::CommandExt;
use std::process::Command;

fn main() {
    // exec never returns on success; the returned Error means the exec failed.
    let _err = Command::new("true").exec();
    std::process::exit(1);
}
