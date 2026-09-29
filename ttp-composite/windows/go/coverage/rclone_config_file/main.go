//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
)

func main() {
	fmt.Printf("COMPOSITE_CASE rclone_config_file\n")
	if !fixture.Begin("rclone_config_file") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\text.txt`, "C:\\Users\\Public\\.config\\rclone\\telemetry-lab-fixture.conf")
	fixture.Success("rclone_config_file")
}
