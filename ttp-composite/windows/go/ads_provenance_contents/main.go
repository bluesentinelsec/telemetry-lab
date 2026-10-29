// Target rule: Unusual File Download from Direct IP Address
// Sigma rule ID: ecb9ed8e-9e96-85bd-a68e-c86d68005053
// Ruleset path: sigma/sysmon/create_stream_hash/create_stream_hash_susp_ip_domains.yml
//go:build windows

package main

import (
	"bytes"
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
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
