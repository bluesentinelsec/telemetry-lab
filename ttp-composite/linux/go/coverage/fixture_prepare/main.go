package main

import (
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
	"os"
)

func main() {
	if !fixture.Begin("fixture_prepare") {
		return
	}
	for _, p := range []string{"/tmp/lab", "/root/.ssh", "/etc/cron.d", "/etc/apt", "/etc/apt/sources.list.d", "/boot"} {
		err := os.Mkdir(p, 0700)
		fixture.Check(err == nil || os.IsExist(err), "fixture directory")
	}
	for _, p := range []string{"/etc/shadow", "/var/log/lab.log", "/root/.bash_history", "/root/.ssh/lab_key", "/usr/bin/lab_old"} {
		files.Write(p)
	}
}
