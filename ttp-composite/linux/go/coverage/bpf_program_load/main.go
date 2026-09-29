package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
	"golang.org/x/sys/unix"
	"runtime"
	"unsafe"
)

func main() {
	if !fixture.Begin("bpf_program_load") {
		return
	}
	insns := [16]byte{0xb7, 0, 0, 0, 0, 0, 0, 0, 0x95}
	license := [4]byte{'G', 'P', 'L', 0}
	attr := [18]uint64{}
	attr[0] = 1 | (2 << 32)
	attr[1] = uint64(uintptr(unsafe.Pointer(&insns[0])))
	attr[2] = uint64(uintptr(unsafe.Pointer(&license[0])))
	fd, _, err := unix.Syscall(unix.SYS_BPF, 5, uintptr(unsafe.Pointer(&attr[0])), uintptr(unsafe.Sizeof(attr)))
	runtime.KeepAlive(insns)
	runtime.KeepAlive(license)
	fixture.Check(err == 0, "BPF program load")
	fixture.Must(unix.Close(int(fd)))
	fmt.Printf("CASE_OK bpf_program_load\n")
}
