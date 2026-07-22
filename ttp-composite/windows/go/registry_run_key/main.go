//go:build windows

// registry_run_key composite (ATT&CK T1547.001) -- Registry Run key persistence.
//
// Sysmon EID 13 (Registry Value Set). Expected ROBUST: Sysmon keys on a value
// written under a Run key (HKCU\...\CurrentVersion\Run), so the write fires the
// event regardless of the runtime that issues it. Uses
// golang.org/x/sys/windows/registry (OpenKey/SetStringValue/DeleteValue) --
// std-only cannot touch the registry without raw advapi32 syscalls, so this is
// the one composite that pulls in x/sys. Benign: the "lab_test" value is set to
// a placeholder path and deleted immediately -- nothing is ever executed.
package main

import "golang.org/x/sys/windows/registry"

func main() {
	k, err := registry.OpenKey(registry.CURRENT_USER,
		`Software\Microsoft\Windows\CurrentVersion\Run`, registry.SET_VALUE)
	if err != nil {
		return
	}
	defer k.Close()

	if err := k.SetStringValue("lab_test", `C:\lab\x.exe`); err != nil {
		return
	}
	k.DeleteValue("lab_test")
}
