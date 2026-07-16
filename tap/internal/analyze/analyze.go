// Package analyze implements the dissertation's cross-runtime comparison over
// normalized events: per-family volume (with ratios), Jaccard symbol-set
// similarity, stable and substrate-specific features, baseline subtraction
// against the `empty` control, and Mann-Whitney U significance (BH-corrected).
//
// Comparisons that use syscall symbol sets (Jaccard, stable, substrate-specific)
// run within an OS, because raw syscall names are not comparable across OSes
// (openat vs NtCreateFile). Volume is reported for every config; cross-OS
// comparison at the semantic-family layer is a later increment.
package analyze

import (
	"bufio"
	"encoding/json"
	"io"
	"sort"

	"github.com/bluesentinelsec/telemetry-lab/tap/internal/model"
	"github.com/bluesentinelsec/telemetry-lab/tap/internal/stat"
)

const controlPrimitive = "empty"

// Result is the full analysis, one entry per primitive.
type Result struct {
	Primitives []PrimitiveResult `json:"primitives"`
}

type PrimitiveResult struct {
	Primitive         string            `json:"primitive"`
	Configs           []ConfigSummary   `json:"configs"`
	Jaccard           []Pair            `json:"jaccard"`             // within-OS, syscall symbols
	StableByOS        map[string][]string `json:"stable_syscalls_by_os"` // in all of an OS's configs
	SubstrateSpecific []ConfigUnique    `json:"substrate_specific"`  // syscalls unique to one config
	Significance      []SigPair         `json:"significance"`        // MWU on total counts, within-OS
}

type ConfigSummary struct {
	Config       string             `json:"config"`
	OS           string             `json:"os"`
	Iterations   int                `json:"iterations"`
	TotalMedian  float64            `json:"total_median"`
	FamilyMedian map[string]float64 `json:"family_median"`
	// BehaviorTotal is total minus the empty control's total for this config
	// (behavior-attributable telemetry). HasBaseline is false if no empty run.
	BehaviorTotal float64 `json:"behavior_total"`
	HasBaseline   bool    `json:"has_baseline"`
}

type Pair struct {
	A, B    string  `json:"-"`
	ConfigA string  `json:"config_a"`
	ConfigB string  `json:"config_b"`
	Jaccard float64 `json:"jaccard"`
}

type ConfigUnique struct {
	Config   string   `json:"config"`
	Syscalls []string `json:"syscalls"`
}

type SigPair struct {
	ConfigA string  `json:"config_a"`
	ConfigB string  `json:"config_b"`
	U       float64 `json:"u"`
	P       float64 `json:"p"`
	PAdj    float64 `json:"p_adjusted"`
	Ratio   float64 `json:"ratio"` // max/min of the two total medians
}

// --- aggregation ---

type runAgg struct {
	familyCount map[model.Family]int
	syscalls    map[string]bool
}

type configAgg struct {
	os       string
	runs     map[string]*runAgg // by run_id
}

// Load reads normalized JSONL and aggregates it into per-primitive,
// per-config, per-run profiles.
func Load(r io.Reader) (map[string]map[string]*configAgg, error) {
	sc := bufio.NewScanner(r)
	sc.Buffer(make([]byte, 0, 1024*1024), 16*1024*1024)
	// primitive -> config -> aggregate
	profiles := map[string]map[string]*configAgg{}
	for sc.Scan() {
		if len(sc.Bytes()) == 0 {
			continue
		}
		var e model.Event
		if err := json.Unmarshal(sc.Bytes(), &e); err != nil {
			return nil, err
		}
		byCfg := profiles[e.Primitive]
		if byCfg == nil {
			byCfg = map[string]*configAgg{}
			profiles[e.Primitive] = byCfg
		}
		agg := byCfg[e.Config]
		if agg == nil {
			agg = &configAgg{os: e.OS, runs: map[string]*runAgg{}}
			byCfg[e.Config] = agg
		}
		run := agg.runs[e.RunID]
		if run == nil {
			run = &runAgg{familyCount: map[model.Family]int{}, syscalls: map[string]bool{}}
			agg.runs[e.RunID] = run
		}
		run.familyCount[e.Family]++
		if e.Family == model.FamilySyscall {
			run.syscalls[e.Name] = true
		}
	}
	return profiles, sc.Err()
}

// Analyze computes the full result from loaded profiles.
func Analyze(profiles map[string]map[string]*configAgg) Result {
	var res Result
	prims := sortedKeys(profiles)
	for _, prim := range prims {
		res.Primitives = append(res.Primitives, analyzePrimitive(prim, profiles[prim], profiles[controlPrimitive]))
	}
	return res
}

func analyzePrimitive(prim string, byCfg map[string]*configAgg, control map[string]*configAgg) PrimitiveResult {
	pr := PrimitiveResult{Primitive: prim, StableByOS: map[string][]string{}}

	// Per-config summaries and the syscall symbol sets.
	symbols := map[string]map[string]bool{} // config -> syscall set (union over runs)
	totals := map[string][]float64{}         // config -> per-run totals
	osOf := map[string]string{}
	for _, cfg := range sortedKeys(byCfg) {
		agg := byCfg[cfg]
		osOf[cfg] = agg.os
		famVals := map[model.Family][]float64{}
		var totalVals []float64
		sym := map[string]bool{}
		for _, run := range agg.runs {
			total := 0
			for fam, n := range run.familyCount {
				famVals[fam] = append(famVals[fam], float64(n))
				total += n
			}
			totalVals = append(totalVals, float64(total))
			for s := range run.syscalls {
				sym[s] = true
			}
		}
		symbols[cfg] = sym
		totals[cfg] = totalVals

		famMed := map[string]float64{}
		for fam, vals := range famVals {
			famMed[string(fam)] = stat.Median(vals)
		}
		cs := ConfigSummary{
			Config: cfg, OS: agg.os, Iterations: len(agg.runs),
			TotalMedian: stat.Median(totalVals), FamilyMedian: famMed,
		}
		if control != nil {
			if ctl, ok := control[cfg]; ok {
				cs.BehaviorTotal = cs.TotalMedian - stat.Median(controlTotals(ctl))
				cs.HasBaseline = true
			}
		}
		pr.Configs = append(pr.Configs, cs)
	}

	configs := sortedKeys(byCfg)

	// Jaccard + significance for within-OS config pairs.
	var pvals []float64
	var sigPairs []SigPair
	for i := 0; i < len(configs); i++ {
		for j := i + 1; j < len(configs); j++ {
			a, b := configs[i], configs[j]
			if osOf[a] != osOf[b] {
				continue // syscall names are not comparable across OSes
			}
			pr.Jaccard = append(pr.Jaccard, Pair{
				ConfigA: a, ConfigB: b, Jaccard: jaccard(symbols[a], symbols[b]),
			})
			u, p := stat.MannWhitneyU(totals[a], totals[b])
			sigPairs = append(sigPairs, SigPair{
				ConfigA: a, ConfigB: b, U: u, P: p, Ratio: ratio(totals[a], totals[b]),
			})
			pvals = append(pvals, p)
		}
	}
	adj := stat.BenjaminiHochberg(pvals)
	for k := range sigPairs {
		sigPairs[k].PAdj = adj[k]
	}
	pr.Significance = sigPairs

	// Stable (per OS) and substrate-specific syscalls.
	byOS := map[string][]string{}
	for _, cfg := range configs {
		byOS[osOf[cfg]] = append(byOS[osOf[cfg]], cfg)
	}
	for os, cfgs := range byOS {
		pr.StableByOS[os] = intersectAll(cfgs, symbols)
	}
	pr.SubstrateSpecific = uniquePerConfig(configs, symbols)

	return pr
}

func controlTotals(ctl *configAgg) []float64 {
	var t []float64
	for _, run := range ctl.runs {
		total := 0
		for _, n := range run.familyCount {
			total += n
		}
		t = append(t, float64(total))
	}
	return t
}

func jaccard(a, b map[string]bool) float64 {
	if len(a) == 0 && len(b) == 0 {
		return 1
	}
	inter, union := 0, len(a)
	for s := range b {
		if a[s] {
			inter++
		} else {
			union++
		}
	}
	if union == 0 {
		return 1
	}
	return float64(inter) / float64(union)
}

// intersectAll returns syscalls present in every one of the given configs.
func intersectAll(configs []string, symbols map[string]map[string]bool) []string {
	if len(configs) == 0 {
		return nil
	}
	counts := map[string]int{}
	for _, cfg := range configs {
		for s := range symbols[cfg] {
			counts[s]++
		}
	}
	var out []string
	for s, c := range counts {
		if c == len(configs) {
			out = append(out, s)
		}
	}
	sort.Strings(out)
	return out
}

// uniquePerConfig returns, per config, the syscalls that appear in no other config.
func uniquePerConfig(configs []string, symbols map[string]map[string]bool) []ConfigUnique {
	counts := map[string]int{}
	for _, cfg := range configs {
		for s := range symbols[cfg] {
			counts[s]++
		}
	}
	var out []ConfigUnique
	for _, cfg := range configs {
		var uniq []string
		for s := range symbols[cfg] {
			if counts[s] == 1 {
				uniq = append(uniq, s)
			}
		}
		if len(uniq) > 0 {
			sort.Strings(uniq)
			out = append(out, ConfigUnique{Config: cfg, Syscalls: uniq})
		}
	}
	return out
}

func ratio(a, b []float64) float64 {
	ma, mb := stat.Median(a), stat.Median(b)
	hi, lo := ma, mb
	if mb > ma {
		hi, lo = mb, ma
	}
	if lo == 0 {
		return 0
	}
	return hi / lo
}

func sortedKeys[V any](m map[string]V) []string {
	out := make([]string, 0, len(m))
	for k := range m {
		out = append(out, k)
	}
	sort.Strings(out)
	return out
}
