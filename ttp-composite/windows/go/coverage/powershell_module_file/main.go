//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"os"
	"path/filepath"
)

func main() {
	fmt.Println("COMPOSITE_CASE powershell_module_file")
	if !fixture.Begin("powershell_module_file") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\text.txt`, filepath.Join(os.Getenv("USERPROFILE"), "Documents\\WindowsPowerShell\\Modules\\TelemetryLabFixture\\TelemetryLabFixture.psm1"))
	fixture.Success("powershell_module_file")
}
