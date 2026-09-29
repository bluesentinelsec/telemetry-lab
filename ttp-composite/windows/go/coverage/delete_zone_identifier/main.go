//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"os"
	"time"
)

func main() {
	fmt.Printf("COMPOSITE_CASE delete_zone_identifier\n")
	if !fixture.Begin("delete_zone_identifier") {
		return
	}
	path := "C:\\lab\\windows-coverage\\work\\download.txt:Zone.Identifier"
	before, err := os.ReadFile(path)
	fixture.Must(err)
	fixture.Check(len(before) > 0 && before[0] == '[', "invalid stream fixture")
	fixture.Must(os.Remove(path))
	// Verify completion, without repeating deletion or retaining probe handles.
	started := time.Now()
	probes := 0
	for {
		after, openErr := os.Open(path)
		probes++
		if openErr == nil {
			fixture.Must(after.Close())
		} else if os.IsNotExist(openErr) {
			break
		} else {
			fixture.Check(os.IsPermission(openErr), "unexpected stream probe error: "+openErr.Error())
		}
		fixture.Check(time.Since(started) < 5*time.Second, "stream deletion did not complete")
		time.Sleep(10 * time.Millisecond)
	}
	fmt.Printf("STREAM_ABSENT probes=%d elapsed_ms=%d\n", probes, time.Since(started).Milliseconds())
	_, err = os.Stat("C:\\lab\\windows-coverage\\work\\download.txt")
	fixture.Must(err)
	fixture.Success("delete_zone_identifier")
}
