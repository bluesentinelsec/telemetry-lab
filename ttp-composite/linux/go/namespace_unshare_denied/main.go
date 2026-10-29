// Target rule: Change namespace privileges via unshare
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
	"golang.org/x/sys/unix"
	"os"
	"runtime"
	"syscall"
)

func main() {
	if !fixture.Begin("namespace_unshare_denied") {
		return
	}
	runtime.LockOSThread()
	defer runtime.UnlockOSThread()
	before, err := os.Stat("/proc/thread-self/ns/net")
	fixture.Must(err)
	fixture.Check(unix.Unshare(unix.CLONE_NEWNET) == unix.EPERM, "expected unprivileged namespace denial")
	after, err := os.Stat("/proc/thread-self/ns/net")
	fixture.Must(err)
	fixture.Check(after.Sys().(*syscall.Stat_t).Ino == before.Sys().(*syscall.Stat_t).Ino, "namespace changed despite denial")
	fmt.Printf("CASE_OK namespace_unshare_denied\n")
}
