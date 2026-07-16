package analyze

import (
	"bytes"
	"encoding/json"
	"fmt"
	"testing"

	"github.com/bluesentinelsec/telemetry-lab/tap/internal/model"
)

// dataset builds a normalized JSONL stream: for each (config, primitive), emit
// `iters` runs, each containing one syscall event per name in `names`.
func dataset(t *testing.T, rows []row) map[string]map[string]*configAgg {
	t.Helper()
	var buf bytes.Buffer
	enc := json.NewEncoder(&buf)
	for _, r := range rows {
		for it := 1; it <= r.iters; it++ {
			runID := fmt.Sprintf("%s/%s/%d", r.config, r.primitive, it)
			for _, name := range r.syscalls {
				e := model.Event{
					OS: r.os, Config: r.config, Primitive: r.primitive,
					Iteration: it, RunID: runID,
					Family: model.FamilySyscall, Name: name,
				}
				if err := enc.Encode(&e); err != nil {
					t.Fatal(err)
				}
			}
		}
	}
	profiles, err := Load(&buf)
	if err != nil {
		t.Fatal(err)
	}
	return profiles
}

type row struct {
	os, config, primitive string
	iters                 int
	syscalls              []string
}

func TestAnalyze(t *testing.T) {
	profiles := dataset(t, []row{
		{"linux", "linux-c-glibc", "empty", 2, []string{"execve", "mmap"}},
		{"linux", "linux-c-musl", "empty", 2, []string{"execve"}},
		{"linux", "linux-c-glibc", "spawn", 2, []string{"execve", "mmap", "clone", "wait4"}},
		{"linux", "linux-c-musl", "spawn", 2, []string{"execve", "clone"}},
	})
	res := Analyze(profiles)

	var spawn *PrimitiveResult
	for i := range res.Primitives {
		if res.Primitives[i].Primitive == "spawn" {
			spawn = &res.Primitives[i]
		}
	}
	if spawn == nil {
		t.Fatal("no spawn result")
	}

	// Volume + baseline subtraction.
	byCfg := map[string]ConfigSummary{}
	for _, c := range spawn.Configs {
		byCfg[c.Config] = c
	}
	if g := byCfg["linux-c-glibc"]; g.TotalMedian != 4 || !g.HasBaseline || g.BehaviorTotal != 2 {
		t.Errorf("glibc spawn: total=%v behavior=%v baseline=%v", g.TotalMedian, g.BehaviorTotal, g.HasBaseline)
	}
	if m := byCfg["linux-c-musl"]; m.TotalMedian != 2 || m.BehaviorTotal != 1 {
		t.Errorf("musl spawn: total=%v behavior=%v", m.TotalMedian, m.BehaviorTotal)
	}

	// Jaccard: {execve,clone} shared / {execve,mmap,clone,wait4} union = 0.5.
	if len(spawn.Jaccard) != 1 || spawn.Jaccard[0].Jaccard != 0.5 {
		t.Errorf("jaccard = %+v, want 0.5", spawn.Jaccard)
	}

	// Stable across both Linux configs: execve, clone.
	stable := spawn.StableByOS["linux"]
	if len(stable) != 2 || stable[0] != "clone" || stable[1] != "execve" {
		t.Errorf("stable = %v, want [clone execve]", stable)
	}

	// Substrate-specific: glibc has mmap, wait4 unique; musl has none.
	var glibcUnique []string
	for _, u := range spawn.SubstrateSpecific {
		if u.Config == "linux-c-glibc" {
			glibcUnique = u.Syscalls
		}
		if u.Config == "linux-c-musl" {
			t.Errorf("musl should have no unique syscalls, got %v", u.Syscalls)
		}
	}
	if len(glibcUnique) != 2 {
		t.Errorf("glibc unique = %v, want [mmap wait4]", glibcUnique)
	}

	// Significance: separated totals -> U=0, ratio 2.
	if len(spawn.Significance) != 1 {
		t.Fatalf("want 1 significance pair, got %d", len(spawn.Significance))
	}
	if s := spawn.Significance[0]; s.U != 0 || s.Ratio != 2 {
		t.Errorf("significance: U=%v ratio=%v", s.U, s.Ratio)
	}
}
