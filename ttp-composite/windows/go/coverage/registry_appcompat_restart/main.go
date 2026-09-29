//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/regops"
)

func main() {
	fmt.Printf("COMPOSITE_CASE registry_appcompat_restart\n")
	if !fixture.Begin("registry_appcompat_restart") {
		return
	}
	regops.SetRegistry("Software\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Layers", "C:\\lab\\windows-coverage\\fixtures\\helper.exe", "REGISTERAPPRESTART")
	fixture.Success("registry_appcompat_restart")
}
