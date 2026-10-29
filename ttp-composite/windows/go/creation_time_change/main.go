// Target rule: File Creation Date Changed to Another Year
// Sigma rule ID: 1117f7b2-3f59-682b-ad07-081d44ae5ddb
// Ruleset path: sigma/sysmon/threat-hunting/file/file_change/file_change_win_date_changed_to_another_year.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"golang.org/x/sys/windows"
	"time"
)

func main() {
	fmt.Print("COMPOSITE_CASE creation_time_change\n")
	if !fixture.Begin("creation_time_change") {
		return
	}

	path, err := windows.UTF16PtrFromString(fixture.Root + `\work\timestamp.txt`)
	fixture.Must(err)
	file, err := windows.CreateFile(path, windows.FILE_READ_ATTRIBUTES|windows.FILE_WRITE_ATTRIBUTES, windows.FILE_SHARE_READ, nil, windows.OPEN_EXISTING, windows.FILE_ATTRIBUTE_NORMAL, 0)
	fixture.Must(err)
	desired := windows.NsecToFiletime(time.Date(2019, 1, 1, 0, 0, 0, 0, time.UTC).UnixNano())
	fixture.Must(windows.SetFileTime(file, &desired, nil, nil))
	var observed windows.Filetime
	fixture.Must(windows.GetFileTime(file, &observed, nil, nil))
	fixture.Check(observed == desired, "creation time differs")
	fixture.Must(windows.CloseHandle(file))

	fixture.Success("creation_time_change")
}
