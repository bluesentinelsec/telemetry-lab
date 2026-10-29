//go:build windows

package fixture

import (
	"fmt"
	"os"
	"path/filepath"
	"time"
)

const Root = `C:\lab\windows-coverage`

func Check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}
func Must(err error) {
	if err != nil {
		panic(err)
	}
}
func Begin(id string) bool {
	Check(os.Getenv("TELEMETRY_LAB_FIXTURE") == "1", "requires isolated lab fixture")
	Check(len(os.Args) == 1 || (len(os.Args) == 2 && os.Args[1] == "--control"), "unexpected arguments")
	if len(os.Args) == 2 {
		fmt.Printf("CONTROL_OK %s\n", id)
		return false
	}
	return true
}
func Success(id string) { fmt.Printf("BEHAVIOR_OK %s\n", id) }
func Hold()             { time.Sleep(5 * time.Second) }
func AppData(suffix string) string {
	app := os.Getenv("APPDATA")
	Check(app != "", "APPDATA missing")
	return filepath.Join(app, suffix)
}
