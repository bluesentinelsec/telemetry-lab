//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
)

func main() {
	fmt.Print("COMPOSITE_CASE public_binary\n")
	if !fixture.Begin("public_binary") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\helper.exe`, `C:\Users\Public\telemetry-lab\fixture.exe`)
	fixture.Success("public_binary")
}
