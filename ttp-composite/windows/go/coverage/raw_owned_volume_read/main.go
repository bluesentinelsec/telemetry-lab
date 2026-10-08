//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"golang.org/x/sys/windows"
	"os"
	"strings"
)

func main() {
	fmt.Print("COMPOSITE_CASE raw_owned_volume_read\n")
	if !fixture.Begin("raw_owned_volume_read") {
		return
	}
	device := os.Getenv("TELEMETRY_LAB_RAW_DEVICE")
	prefix := `\\.\PhysicalDrive`
	fixture.Check(strings.HasPrefix(device, prefix) && len(device) > len(prefix), "invalid owned device")
	for _, c := range device[len(prefix):] {
		fixture.Check(c >= '0' && c <= '9', "invalid device number")
	}
	path, err := windows.UTF16PtrFromString(device)
	fixture.Must(err)
	h, err := windows.CreateFile(path, windows.GENERIC_READ, windows.FILE_SHARE_READ|windows.FILE_SHARE_WRITE, nil, windows.OPEN_EXISTING, 0, 0)
	fixture.Must(err)
	data := make([]byte, 512)
	var n uint32
	fixture.Must(windows.ReadFile(h, data, &n, nil))
	fixture.Must(windows.CloseHandle(h))
	fixture.Check(n == 512, "short raw read")
	for i, b := range data {
		fixture.Check(b == byte(i%251), "raw fixture differs")
	}
	fixture.Success("raw_owned_volume_read")
}
