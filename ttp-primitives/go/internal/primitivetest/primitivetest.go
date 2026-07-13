// Package primitivetest provides the shared assertion for TTP primitives.
//
// A primitive passes when its compiled binary runs to completion and exits 0.
// The binary is built rather than run via "go run" so that the test exercises
// the same artifact the experiment will execute, under whatever toolchain
// settings (GOOS, GOARCH, CGO_ENABLED) the environment specifies.
package primitivetest

import (
	"errors"
	"os/exec"
	"path/filepath"
	"runtime"
	"testing"
)

// ExitsZero builds the package in the calling test's directory and asserts that
// the resulting binary exits 0.
func ExitsZero(t *testing.T) {
	t.Helper()

	bin := filepath.Join(t.TempDir(), "primitive")
	if runtime.GOOS == "windows" {
		bin += ".exe"
	}

	if out, err := exec.Command("go", "build", "-o", bin, ".").CombinedOutput(); err != nil {
		t.Fatalf("build failed: %v\n%s", err, out)
	}

	err := exec.Command(bin).Run()
	if err == nil {
		return
	}

	var exit *exec.ExitError
	if errors.As(err, &exit) {
		t.Fatalf("expected exit code 0, got %d", exit.ExitCode())
	}
	t.Fatalf("could not run %s: %v", bin, err)
}
