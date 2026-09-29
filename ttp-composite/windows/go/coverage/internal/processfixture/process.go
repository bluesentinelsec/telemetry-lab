//go:build windows

package processfixture

import (
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"golang.org/x/sys/windows"
	"os/exec"
	"strings"
	"syscall"
	"time"
	"unsafe"
)

func Run(remote bool) {
	cmd := exec.Command(`C:\Windows\System32\ping.exe`, "-n", "10", "-w", "1000", "127.0.0.1")
	cmd.SysProcAttr = &syscall.SysProcAttr{CreationFlags: 0x08000000}
	fixture.Must(cmd.Start())
	defer func() { _ = cmd.Process.Kill(); _ = cmd.Wait() }()
	time.Sleep(200 * time.Millisecond)
	target, err := windows.OpenProcess(0x1fffff, false, uint32(cmd.Process.Pid))
	fixture.Must(err)
	defer windows.CloseHandle(target)
	pid, err := windows.GetProcessId(target)
	fixture.Must(err)
	fixture.Check(pid == uint32(cmd.Process.Pid), "target PID")
	if !remote {
		return
	}
	kernel := windows.NewLazySystemDLL("kernel32.dll")
	local := kernel.NewProc("GetCurrentProcessId").Addr()
	var owner windows.Handle
	ok, _, _ := kernel.NewProc("GetModuleHandleExW").Call(6, local, uintptr(unsafe.Pointer(&owner)))
	fixture.Check(ok != 0, "module owner")
	var filename [260]uint16
	n, _, _ := kernel.NewProc("GetModuleFileNameW").Call(uintptr(owner), uintptr(unsafe.Pointer(&filename[0])), 260)
	fixture.Check(n > 0 && n < 260, "module filename")
	name := windows.UTF16ToString(filename[:])
	name = name[strings.LastIndex(name, `\`)+1:]
	snap, err := windows.CreateToolhelp32Snapshot(windows.TH32CS_SNAPMODULE, pid)
	fixture.Must(err)
	defer windows.CloseHandle(snap)
	var me windows.ModuleEntry32
	me.Size = uint32(unsafe.Sizeof(me))
	err = windows.Module32First(snap, &me)
	var base uintptr
	for err == nil {
		if strings.EqualFold(windows.UTF16ToString(me.Module[:]), name) {
			base = me.ModBaseAddr
			break
		}
		err = windows.Module32Next(snap, &me)
	}
	fixture.Check(base != 0, "remote module missing")
	thread, _, _ := kernel.NewProc("CreateRemoteThread").Call(uintptr(target), 0, 0, base+local-uintptr(owner), 0, 0, 0)
	fixture.Check(thread != 0, "remote thread creation")
	defer windows.CloseHandle(windows.Handle(thread))
	wait, err := windows.WaitForSingleObject(windows.Handle(thread), 5000)
	fixture.Must(err)
	fixture.Check(wait == windows.WAIT_OBJECT_0, "remote thread timeout")
	var code uint32
	ok, _, _ = kernel.NewProc("GetExitCodeThread").Call(thread, uintptr(unsafe.Pointer(&code)))
	fixture.Check(ok != 0 && code == pid, "remote benign function result")
}
