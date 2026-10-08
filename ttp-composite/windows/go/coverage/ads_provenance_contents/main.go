//go:build windows

package main

import (
	"bytes"
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"os"
)

func main() {
	fmt.Print("COMPOSITE_CASE ads_provenance_contents\n")
	if !fixture.Begin("ads_provenance_contents") {
		return
	}
	path := fixture.Root + `\work\provenance.exe:Zone.Identifier`
	data := []byte("[ZoneTransfer]\r\nZoneId=3\r\nHostUrl=http://192.0.2.1/fixture.exe\r\n")
	fixture.Must(os.WriteFile(path, data, 0600))
	actual, err := os.ReadFile(path)
	fixture.Must(err)
	fixture.Check(bytes.Equal(actual, data), "stream bytes differ")
	fixture.Success("ads_provenance_contents")
}
