package fixture

import (
	"fmt"
	"os"
	"time"
)

const Payload = "telemetry-lab-fixture\n"

func Check(ok bool, description string) {
	if !ok {
		panic(description)
	}
}
func Must(err error) {
	if err != nil {
		panic(err)
	}
}
func Begin(id string) bool {
	_, err := os.Stat("/.dockerenv")
	Must(err)
	Check(os.Getenv("TELEMETRY_LAB_FIXTURE") == "1", "requires isolated lab fixture")
	Check(len(os.Args) == 1 || (len(os.Args) == 2 && os.Args[1] == "--control"), "unexpected arguments")
	time.AfterFunc(10*time.Second, func() { fmt.Fprintln(os.Stderr, "FAIL fixture deadline"); os.Exit(1) })
	if len(os.Args) == 2 {
		fmt.Printf("CONTROL_OK %s\n", id)
		return false
	}
	return true
}
