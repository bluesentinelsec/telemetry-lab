//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"golang.org/x/sys/windows"
	"strings"
	"unsafe"
)

func main() {
	fmt.Print("COMPOSITE_CASE signed_system_library_load\n")
	if !fixture.Begin("signed_system_library_load") {
		return
	}
	name, _ := windows.UTF16PtrFromString("RstrtMgr.dll")
	kernel := windows.NewLazySystemDLL("kernel32.dll")
	before, _, _ := kernel.NewProc("GetModuleHandleW").Call(uintptr(unsafe.Pointer(name)))
	fixture.Check(before == 0, "module already loaded")
	dll, err := windows.LoadDLL(`C:\Windows\System32\RstrtMgr.dll`)
	fixture.Must(err)
	var path [260]uint16
	n, _, _ := kernel.NewProc("GetModuleFileNameW").Call(uintptr(dll.Handle), uintptr(unsafe.Pointer(&path[0])), uintptr(len(path)))
	fixture.Check(n > 0 && n < uintptr(len(path)) && strings.EqualFold(windows.UTF16ToString(path[:]), `C:\Windows\System32\RstrtMgr.dll`), "loaded module differs")
	fixture.Must(dll.Release())
	fixture.Success("signed_system_library_load")
}
