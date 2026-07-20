package report

import (
	"strings"
	"testing"

	"github.com/bluesentinelsec/telemetry-lab/tap/internal/analyze"
)

func TestProvenanceSectionOmittedWhenNil(t *testing.T) {
	out := Render(analyze.Result{})
	if strings.Contains(out, "## Provenance") {
		t.Fatalf("provenance section should be omitted when Result.Provenance is nil")
	}
}

func TestProvenanceSectionRendered(t *testing.T) {
	r := analyze.Result{Provenance: &analyze.Provenance{
		Generated:           "2026-07-20T19:02:56Z",
		Host:                "linux",
		OS:                  "Debian GNU/Linux 13 (trixie)",
		Kernel:              "6.12.95",
		TelemetryLabRelease: "0.1.0",
		Components: []analyze.ProvenanceComponent{
			{Name: "falco", Type: "detector", Version: "0.44.1", SHA256: "5bfd1570e4571ab661dc", Path: "/usr/bin/falco"},
			{Name: "ttp_primitives", Type: "project", Version: "0.1.0", SHA256: "", Path: "/opt/lab/x/ttp-primitives"},
		},
	}}
	out := Render(r)
	for _, want := range []string{"## Provenance", "0.44.1", "falco", "telemetry-lab release 0.1.0", "5bfd1570e457"} {
		if !strings.Contains(out, want) {
			t.Errorf("report missing %q\n--- report ---\n%s", want, out)
		}
	}
	// long sha is truncated; empty sha renders as a dash.
	if strings.Contains(out, "5bfd1570e4571ab661dc |") {
		t.Errorf("sha-256 should be truncated in the table")
	}
}
