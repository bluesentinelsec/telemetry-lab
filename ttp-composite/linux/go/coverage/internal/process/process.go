package process

import (
	"bytes"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
	"golang.org/x/sys/unix"
	"io"
	"os"
	"os/exec"
	"runtime"
	"syscall"
)

func ExecuteHelper(path string, memory bool) {
	var f *os.File
	var err error
	if memory {
		fd, e := unix.MemfdCreate("lab-helper", 0)
		fixture.Must(e)
		f = os.NewFile(uintptr(fd), "lab-helper")
	} else {
		f, err = os.OpenFile(path, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0700)
		fixture.Must(err)
	}
	src, err := os.Open("/opt/coverage/helper")
	fixture.Must(err)
	_, err = io.Copy(f, src)
	fixture.Must(err)
	fixture.Must(src.Close())
	fixture.Must(f.Chmod(0700))
	var cmd *exec.Cmd
	if memory {
		// Go has no fexecve wrapper. ExtraFiles keeps the memfd at fd 3 in the
		// child; exec through /proc/self/fd/3 still executes the in-memory file.
		defer f.Close()
		cmd = exec.Command("/proc/self/fd/3")
		cmd.Args[0] = "lab-helper"
		cmd.ExtraFiles = []*os.File{f}
	} else {
		fixture.Must(f.Close())
		defer os.Remove(path)
		cmd = exec.Command(path)
	}
	data, err := cmd.Output()
	fixture.Must(err)
	fixture.Check(bytes.Equal(data, []byte("HELPER_OK\n")), "helper completion")
}
func Attach() {
	// Linux ptrace ownership is per OS thread, not per Go goroutine.
	runtime.LockOSThread()
	defer runtime.UnlockOSThread()
	cmd := exec.Command("/bin/sleep", "10")
	fixture.Must(cmd.Start())
	defer cmd.Process.Kill()
	pid := cmd.Process.Pid
	fixture.Must(unix.PtraceAttach(pid))
	var status unix.WaitStatus
	got, err := unix.Wait4(pid, &status, 0, nil)
	fixture.Must(err)
	fixture.Check(got == pid && status.Stopped(), "child tracing stop")
	fixture.Must(unix.PtraceDetach(pid))
	fixture.Must(cmd.Process.Signal(syscall.SIGTERM))
	err = cmd.Wait()
	fixture.Check(err != nil, "child must terminate by SIGTERM")
	st, ok := cmd.ProcessState.Sys().(syscall.WaitStatus)
	fixture.Check(ok && st.Signaled() && st.Signal() == syscall.SIGTERM, "child termination")
}
func TraceMe() {
	runtime.LockOSThread()
	defer runtime.UnlockOSThread()
	// Go's fork/exec path issues PTRACE_TRACEME in the child before exec.
	// The same benign helper provides a checked child completion.
	cmd := exec.Command("/opt/coverage/helper")
	cmd.SysProcAttr = &syscall.SysProcAttr{Ptrace: true}
	var output bytes.Buffer
	cmd.Stdout = &output
	fixture.Must(cmd.Start())
	defer cmd.Process.Kill()
	var status unix.WaitStatus
	got, err := unix.Wait4(cmd.Process.Pid, &status, 0, nil)
	fixture.Must(err)
	fixture.Check(got == cmd.Process.Pid && status.Stopped() && status.StopSignal() == syscall.SIGTRAP, "traceme exec stop")
	fixture.Must(unix.PtraceDetach(cmd.Process.Pid))
	fixture.Must(cmd.Wait())
	fixture.Check(output.String() == "HELPER_OK\n", "traced child completion")
}
