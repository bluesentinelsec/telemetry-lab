//go:build windows

package main

// process_enumeration primitive (Windows): enumerate running processes.
//
// The Linux reference walks /proc; the Windows equivalent is a Toolhelp process
// snapshot (CreateToolhelp32Snapshot + Process32First/Next), which reads the
// kernel's process table. Go's syscall package wraps these directly, so no cgo
// or third-party dependency is needed; the cgo/static substrate split lives in
// anchor_cgo.go. Self-contained and read-only: it counts the live processes and
// exits 0 as long as at least itself is visible.

import (
	"os"
	"syscall"
	"unsafe"
)

func main() {
	snap, err := syscall.CreateToolhelp32Snapshot(syscall.TH32CS_SNAPPROCESS, 0)
	if err != nil {
		os.Exit(1)
	}
	defer syscall.CloseHandle(snap)

	var pe syscall.ProcessEntry32
	pe.Size = uint32(unsafe.Sizeof(pe))
	if err := syscall.Process32First(snap, &pe); err != nil {
		os.Exit(1)
	}
	procs := 0
	for {
		procs++
		if err := syscall.Process32Next(snap, &pe); err != nil {
			break
		}
	}
	if procs == 0 {
		os.Exit(1)
	}
}
