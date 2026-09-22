//go:build windows

package main

import (
	"bytes"
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"golang.org/x/sys/windows"
)

func main() {
	fmt.Print("COMPOSITE_CASE named_pipe_indicator\n")
	if !fixture.Begin("named_pipe_indicator") {
		return
	}

	path, err := windows.UTF16PtrFromString(`\\.\pipe\testPipe`)
	fixture.Must(err)
	server, err := windows.CreateNamedPipe(path, windows.PIPE_ACCESS_DUPLEX|windows.FILE_FLAG_FIRST_PIPE_INSTANCE, windows.PIPE_TYPE_BYTE|windows.PIPE_READMODE_BYTE|windows.PIPE_WAIT, 1, 1024, 1024, 5000, nil)
	fixture.Must(err)
	client, err := windows.CreateFile(path, windows.GENERIC_READ|windows.GENERIC_WRITE, 0, nil, windows.OPEN_EXISTING, 0, 0)
	fixture.Must(err)
	err = windows.ConnectNamedPipe(server, nil)
	fixture.Check(err == nil || err == windows.ERROR_PIPE_CONNECTED, "pipe connection failed")
	payload := []byte("telemetry-lab\x00")
	reply := make([]byte, len(payload))
	var n uint32
	fixture.Must(windows.WriteFile(client, payload, &n, nil))
	fixture.Check(int(n) == len(payload), "short pipe write")
	fixture.Must(windows.ReadFile(server, reply, &n, nil))
	fixture.Check(int(n) == len(payload) && bytes.Equal(payload, reply), "pipe request differs")
	fixture.Must(windows.WriteFile(server, reply, &n, nil))
	fixture.Check(int(n) == len(payload), "short pipe reply")
	fixture.Must(windows.ReadFile(client, reply, &n, nil))
	fixture.Check(int(n) == len(payload) && bytes.Equal(payload, reply), "pipe response differs")
	fixture.Must(windows.CloseHandle(client))
	fixture.Must(windows.DisconnectNamedPipe(server))
	fixture.Must(windows.CloseHandle(server))

	fixture.Success("named_pipe_indicator")
}
