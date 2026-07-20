package analyze

import (
	"os"
	"path/filepath"
	"testing"
)

func TestLoadProvenance(t *testing.T) {
	dir := t.TempDir()
	js := `{"generated":"2026-07-20T19:02:56Z","host":"linux",` +
		`"os":"Debian GNU/Linux 13 (trixie)","kernel":"6.12.95",` +
		`"telemetry_lab_release":"0.1.0","components":[` +
		`{"name":"falco","type":"detector","version":"0.44.1","sha256":"5bfd","path":"/usr/bin/falco"},` +
		`{"name":"ttp_primitives","type":"project","version":"0.1.0","sha256":null,"path":"/opt/lab/x/ttp-primitives"}]}`
	if err := os.WriteFile(filepath.Join(dir, "inventory.json"), []byte(js), 0o644); err != nil {
		t.Fatal(err)
	}

	// (a) directory input finds inventory.json inside it.
	p, err := LoadProvenance(dir)
	if err != nil {
		t.Fatalf("dir input: %v", err)
	}
	if p == nil || p.Host != "linux" || p.TelemetryLabRelease != "0.1.0" || len(p.Components) != 2 {
		t.Fatalf("dir input: unexpected %+v", p)
	}
	// a JSON null sha256 must decode to the empty string, not fail.
	if p.Components[1].SHA256 != "" {
		t.Errorf("null sha256 should decode to empty string, got %q", p.Components[1].SHA256)
	}

	// (b) file input finds inventory.json in the file's directory.
	f := filepath.Join(dir, "normalized.jsonl")
	if err := os.WriteFile(f, []byte("{}\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	p2, err := LoadProvenance(f)
	if err != nil || p2 == nil || p2.Host != "linux" {
		t.Fatalf("file input: err=%v prov=%+v", err, p2)
	}

	// (c) no inventory.json → (nil, nil), not an error.
	p3, err := LoadProvenance(t.TempDir())
	if err != nil {
		t.Fatalf("absent: unexpected error %v", err)
	}
	if p3 != nil {
		t.Fatalf("absent: expected nil provenance, got %+v", p3)
	}
}
