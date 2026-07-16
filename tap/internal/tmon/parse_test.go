package tmon

import (
	"os"
	"testing"
)

func parseFixture(t *testing.T, name string) *Execution {
	t.Helper()
	f, err := os.Open("../../testdata/" + name)
	if err != nil {
		t.Fatalf("open fixture: %v", err)
	}
	defer f.Close()
	ex, err := Parse(f)
	if err != nil {
		t.Fatalf("parse: %v", err)
	}
	return ex
}

func TestParseLinux(t *testing.T) {
	ex := parseFixture(t, "linux_read.jsonl")
	if ex.OS != "linux" {
		t.Errorf("OS = %q, want linux", ex.OS)
	}
	if ex.Meta["language"] != "c" || ex.Meta["runtime"] != "glibc" {
		t.Errorf("provenance not parsed: %v", ex.Meta)
	}
	if len(ex.Events) != 9 {
		t.Errorf("events = %d, want 9", len(ex.Events))
	}
	if !ex.HasSummary {
		t.Error("missing summary")
	}
	if d, ok := ex.Dropped(); !ok || d != 0 {
		t.Errorf("Dropped = (%d,%v), want (0,true)", d, ok)
	}
}

func TestParseWindows(t *testing.T) {
	ex := parseFixture(t, "windows_read.jsonl")
	if ex.OS != "windows" {
		t.Errorf("OS = %q, want windows", ex.OS)
	}
	if ex.Meta["runtime"] != "ucrt" {
		t.Errorf("runtime = %q, want ucrt", ex.Meta["runtime"])
	}
	if len(ex.Events) != 7 {
		t.Errorf("events = %d, want 7", len(ex.Events))
	}
}
