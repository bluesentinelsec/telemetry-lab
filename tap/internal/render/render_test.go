package render

import (
	"os"
	"testing"

	"github.com/bluesentinelsec/telemetry-lab/tap/internal/analyze"
)

func TestRenderProducesPNGs(t *testing.T) {
	r := analyze.Result{Primitives: []analyze.PrimitiveResult{{
		Primitive: "spawn",
		Configs: []analyze.ConfigSummary{
			{Config: "linux-c-glibc", OS: "linux", TotalMedian: 10, HasBaseline: true, BehaviorTotal: 6},
			{Config: "linux-c-musl", OS: "linux", TotalMedian: 5, HasBaseline: true, BehaviorTotal: 3},
		},
		Jaccard: []analyze.Pair{{ConfigA: "linux-c-glibc", ConfigB: "linux-c-musl", Jaccard: 0.5}},
	}}}
	dir := t.TempDir()
	files, err := Render(r, dir)
	if err != nil {
		t.Fatalf("render: %v", err)
	}
	// volume + baseline + one heatmap = 3 figures.
	if len(files) != 3 {
		t.Fatalf("figures = %d, want 3", len(files))
	}
	for _, f := range files {
		info, err := os.Stat(f)
		if err != nil || info.Size() == 0 {
			t.Errorf("figure %s missing or empty", f)
		}
	}
}
