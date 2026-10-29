// Target rule: Hidden Executable In NTFS Alternate Data Stream
// Sigma rule ID: e5cca2eb-74d0-c45b-ec14-3c09f568f8c0
// Ruleset path: sigma/sysmon/create_stream_hash/create_stream_hash_ads_executable.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
)

func main() {
	fmt.Print("COMPOSITE_CASE ads_executable\n")
	if !fixture.Begin("ads_executable") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\helper.exe`, `C:\lab\windows-coverage\work\carrier.txt:fixture.exe`)
	fixture.Success("ads_executable")
}
