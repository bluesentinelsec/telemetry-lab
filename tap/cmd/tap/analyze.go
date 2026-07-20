package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"sort"

	"github.com/bluesentinelsec/telemetry-lab/tap/internal/analyze"
)

func runAnalyze(args []string) error {
	out := "analysis.json"
	primFilter := ""
	var input string
	for i := 0; i < len(args); i++ {
		switch args[i] {
		case "-o", "--output":
			if i+1 >= len(args) {
				return fmt.Errorf("-o expects a path")
			}
			i++
			out = args[i]
		case "--primitive":
			if i+1 >= len(args) {
				return fmt.Errorf("--primitive expects a value")
			}
			i++
			primFilter = args[i]
		default:
			input = args[i]
		}
	}
	if input == "" {
		return fmt.Errorf("analyze needs a normalized.jsonl input")
	}

	f, err := os.Open(input)
	if err != nil {
		return err
	}
	defer f.Close()
	profiles, err := analyze.Load(f)
	if err != nil {
		return err
	}
	result := analyze.Analyze(profiles)
	attachProvenance(&result, input)

	of, err := os.Create(out)
	if err != nil {
		return err
	}
	defer of.Close()
	w := bufio.NewWriter(of)
	enc := json.NewEncoder(w)
	enc.SetIndent("", "  ")
	if err := enc.Encode(&result); err != nil {
		return err
	}
	if err := w.Flush(); err != nil {
		return err
	}

	printAnalysis(result, primFilter, out)
	return nil
}

func printAnalysis(r analyze.Result, primFilter, out string) {
	fmt.Printf("tap analyze: %d primitives → %s\n\n", len(r.Primitives), out)
	for _, p := range r.Primitives {
		if primFilter != "" && p.Primitive != primFilter {
			continue
		}
		fmt.Printf("== %s ==\n", p.Primitive)

		fmt.Println("  VOLUME (median events/run · behavior = minus empty control)")
		cfgs := append([]analyze.ConfigSummary(nil), p.Configs...)
		sort.Slice(cfgs, func(i, j int) bool { return cfgs[i].TotalMedian > cfgs[j].TotalMedian })
		for _, c := range cfgs {
			behav := "n/a"
			if c.HasBaseline {
				behav = fmt.Sprintf("%.0f", c.BehaviorTotal)
			}
			fmt.Printf("    %-22s total=%-6.0f behavior=%-5s (%d iters)\n",
				c.Config, c.TotalMedian, behav, c.Iterations)
		}

		if len(p.Jaccard) > 0 {
			hi, lo := p.Jaccard[0], p.Jaccard[0]
			for _, j := range p.Jaccard {
				if j.Jaccard > hi.Jaccard {
					hi = j
				}
				if j.Jaccard < lo.Jaccard {
					lo = j
				}
			}
			fmt.Printf("  SYMBOL OVERLAP (Jaccard, syscalls, within-OS)\n")
			fmt.Printf("    highest %s↔%s %.2f · lowest %s↔%s %.2f\n",
				hi.ConfigA, hi.ConfigB, hi.Jaccard, lo.ConfigA, lo.ConfigB, lo.Jaccard)
		}
		for os, stable := range p.StableByOS {
			fmt.Printf("  STABLE syscalls across all %s configs: %d\n", os, len(stable))
		}
		if len(p.Significance) > 0 {
			fmt.Println("  SIGNIFICANCE (Mann-Whitney U on total counts, BH-corrected)")
			for _, s := range p.Significance {
				fmt.Printf("    %s vs %s: ratio=%.1f× p=%.3g (adj %.3g)\n",
					s.ConfigA, s.ConfigB, s.Ratio, s.P, s.PAdj)
			}
		}
		fmt.Println()
	}
}
