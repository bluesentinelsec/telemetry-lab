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
	fmt.Println("COMPOSITE_CASE rclone_config_file")
	if !fixture.Begin("rclone_config_file") {
		return
	}
	files.CopyVerified(fixture.Root+`\fixtures\text.txt`, filepath.Join(os.Getenv("USERPROFILE"), ".config\\rclone\\telemetry-lab-fixture.conf"))
	fixture.Success("rclone_config_file")
}
