package report

import (
	"strings"
	"testing"

	"github.com/bluesentinelsec/telemetry-lab/tap/internal/analyze"
)

func TestReportHasAllResearchQuestions(t *testing.T) {
	r := analyze.Result{Primitives: []analyze.PrimitiveResult{{
		Primitive: "spawn",
		Configs: []analyze.ConfigSummary{{
			Config: "linux-c-glibc", OS: "linux", TotalMedian: 10,
			FamilyMedian: map[string]float64{"syscall": 8, "process": 2},
			HasBaseline:  true, BehaviorTotal: 4,
		}},
		Jaccard:    []analyze.Pair{{ConfigA: "linux-c-glibc", ConfigB: "linux-c-musl", Jaccard: 0.5}},
		StableByOS: map[string][]string{"linux": {"execve", "clone"}},
		CrossOS: []analyze.CrossOSFamily{{
			Family: "file", LinuxMedian: 2, WindowsMedian: 1, Shared: []string{"open"},
		}},
	}}}
	md := Render(r)
	for _, want := range []string{"RQ1", "RQ2", "RQ3", "RQ4", "spawn", "linux-c-glibc", "runtime overhead"} {
		if !strings.Contains(md, want) {
			t.Errorf("report missing %q", want)
		}
	}
}
