package tmon

import (
	"encoding/json"
	"os"
	"strings"
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

// The old cJSON writer emitted large rt_sigreturn register values as rounded
// exponential numbers. Keep the original numeric token, including its precision
// limitation, rather than rejecting a complete run or silently rounding again.
func TestParseLargeReturnNumbers(t *testing.T) {
	for _, token := range []string{"3.325580565611095e+18", "-6.77971522612429e+18", "9223372036854775807", "-9223372036854775808", "9007199254740993", "-1"} {
		t.Run(token, func(t *testing.T) {
			ex, err := Parse(strings.NewReader(`{"record":"event","kind":"syscall","syscall":"rt_sigreturn","ret":` + token + `}`))
			if err != nil {
				t.Fatal(err)
			}
			if ex.Events[0].Ret == nil || ex.Events[0].Ret.String() != token {
				t.Fatalf("return token changed: %v", ex.Events[0].Ret)
			}
			encoded, err := json.Marshal(ex.Events[0].Ret)
			if err != nil || string(encoded) != token {
				t.Fatalf("numeric round trip: %s, %v", encoded, err)
			}
		})
	}
}
