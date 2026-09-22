//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"golang.org/x/sys/windows"
	"golang.org/x/sys/windows/registry"
)

func main() {
	fmt.Print("COMPOSITE_CASE registry_runmru_delete\n")
	if !fixture.Begin("registry_runmru_delete") {
		return
	}

	path := `Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU`
	// The harness seeds a leaf key; DeleteKey removes that key and its values.
	fixture.Must(registry.DeleteKey(registry.CURRENT_USER, path))
	key, err := registry.OpenKey(registry.CURRENT_USER, path, registry.READ)
	if err == nil {
		key.Close()
	}
	fixture.Check(err == windows.ERROR_FILE_NOT_FOUND, "RunMRU still exists")

	fixture.Success("registry_runmru_delete")
}
