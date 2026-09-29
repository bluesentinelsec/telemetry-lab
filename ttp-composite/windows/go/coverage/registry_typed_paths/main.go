//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/regops"
)

func main() {
	fmt.Println("COMPOSITE_CASE registry_typed_paths")
	if !fixture.Begin("registry_typed_paths") {
		return
	}
	regops.SetRegistry("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\TypedPaths", "url99", "C:\\lab\\windows-coverage\\work")
	fixture.Success("registry_typed_paths")
}
