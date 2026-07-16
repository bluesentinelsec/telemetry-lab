package normalize

import (
	"os"
	"testing"

	"github.com/bluesentinelsec/telemetry-lab/tap/internal/model"
	"github.com/bluesentinelsec/telemetry-lab/tap/internal/tmon"
)

func load(t *testing.T, name string) ([]model.Event, model.ExecutionSummary) {
	t.Helper()
	f, err := os.Open("../../testdata/" + name)
	if err != nil {
		t.Fatalf("open: %v", err)
	}
	defer f.Close()
	ex, err := tmon.Parse(f)
	if err != nil {
		t.Fatalf("parse: %v", err)
	}
	events, sum, err := Normalize(ex)
	if err != nil {
		t.Fatalf("normalize: %v", err)
	}
	return events, sum
}

func find(events []model.Event, fam model.Family, name string) *model.Event {
	for i := range events {
		if events[i].Family == fam && events[i].Name == name {
			return &events[i]
		}
	}
	return nil
}

func TestNormalizeLinuxFamilies(t *testing.T) {
	events, sum := load(t, "linux_read.jsonl")

	want := map[model.Family]int{
		model.FamilySyscall: 6, // execve, 3×openat, connect, read
		model.FamilyProcess: 3, // fork, exec, exit
		model.FamilyFile:    2, // /etc/hostname, /no/such/file (not the .so)
		model.FamilyLibrary: 1, // libc.so.6
		model.FamilyNetwork: 1, // connect
	}
	for fam, n := range want {
		if sum.FamilyCounts[fam] != n {
			t.Errorf("family %s = %d, want %d", fam, sum.FamilyCounts[fam], n)
		}
	}

	// A .so open is a library load, not a file event.
	if lib := find(events, model.FamilyLibrary, "load"); lib == nil || lib.Attrs["path"] != "/lib/x86_64-linux-gnu/libc.so.6" {
		t.Errorf("library load event wrong: %+v", lib)
	}
	// The connect carries its decoded endpoint.
	if net := find(events, model.FamilyNetwork, "connect"); net == nil || net.Attrs["remote"] != "127.0.0.1:9999" {
		t.Errorf("network connect event wrong: %+v", net)
	}
	// The raw syscall keeps its result.
	if sc := find(events, model.FamilySyscall, "connect"); sc == nil || sc.Attrs["error"] != "ECONNREFUSED" {
		t.Errorf("syscall connect attrs wrong: %+v", sc)
	}
}

func TestNormalizeLinuxProvenanceAndTime(t *testing.T) {
	events, sum := load(t, "linux_read.jsonl")
	if sum.Config != "linux-c-glibc" {
		t.Errorf("config = %q, want linux-c-glibc", sum.Config)
	}
	if sum.RunID != "linux-c-glibc/read_file/1" {
		t.Errorf("run_id = %q", sum.RunID)
	}
	// First event's timestamp is rebased to 0.
	if events[0].TimeNs != 0 {
		t.Errorf("first event time = %d, want 0", events[0].TimeNs)
	}
	if events[0].OS != "linux" || events[0].Runtime != "glibc" {
		t.Errorf("provenance not stamped on events: %+v", events[0])
	}
}

func TestNormalizeWindowsFamilies(t *testing.T) {
	events, sum := load(t, "windows_read.jsonl")
	want := map[model.Family]int{
		model.FamilySyscall:  1,
		model.FamilyProcess:  2, // start, stop
		model.FamilyLibrary:  1, // image load
		model.FamilyFile:     1,
		model.FamilyNetwork:  1,
		model.FamilyRegistry: 1,
	}
	for fam, n := range want {
		if sum.FamilyCounts[fam] != n {
			t.Errorf("family %s = %d, want %d", fam, sum.FamilyCounts[fam], n)
		}
	}
	if reg := find(events, model.FamilyRegistry, "query_value"); reg == nil ||
		reg.Attrs["key"] != `HKLM\Software\Foo` || reg.Attrs["value"] != "Bar" {
		t.Errorf("registry event wrong: %+v", reg)
	}
	if net := find(events, model.FamilyNetwork, "connect"); net == nil || net.Attrs["remote"] != "1.2.3.4:80" {
		t.Errorf("network event wrong: %+v", net)
	}
}

func TestExcludeDroppedRun(t *testing.T) {
	_, sum := load(t, "linux_dropped.jsonl")
	if !sum.Excluded {
		t.Fatal("run with dropped events should be excluded")
	}
	if sum.Config != "linux-c-musl" {
		t.Errorf("config = %q, want linux-c-musl", sum.Config)
	}
}
