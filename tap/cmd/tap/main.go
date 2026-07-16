// Command tap is the telemetry analysis pipeline for the telemetry-lab study.
// It turns raw tmon JSONL (eBPF on Linux, ETW on Windows) into the normalized
// common schema and, in later stages, the cross-runtime comparisons that answer
// the dissertation's research questions. This build implements `normalize` and
// `inspect`.
package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"github.com/bluesentinelsec/telemetry-lab/tap/internal/model"
	"github.com/bluesentinelsec/telemetry-lab/tap/internal/normalize"
	"github.com/bluesentinelsec/telemetry-lab/tap/internal/tmon"
)

const usage = `tap — telemetry analysis pipeline

Usage:
  tap run       <raw-dir> -o <results-dir>             All stages end-to-end
  tap normalize <raw-dir|file> [-o normalized.jsonl]   Raw tmon JSONL -> common schema
  tap analyze   <normalized.jsonl> [-o analysis.json] [--primitive X]
  tap render    <analysis.json> [-o figures/]          PNG figures
  tap report    <analysis.json> [-o report.md]         Findings by research question
  tap inspect   <file.jsonl>                            Human summary of one artifact
  tap version

Raw inputs are self-describing: provenance (os, language, compiler, runtime,
primitive, iteration) is read from each tmon file's meta record.`

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintln(os.Stderr, usage)
		os.Exit(2)
	}
	var err error
	switch os.Args[1] {
	case "normalize":
		err = runNormalize(os.Args[2:])
	case "analyze":
		err = runAnalyze(os.Args[2:])
	case "render":
		err = runRender(os.Args[2:])
	case "report":
		err = runReport(os.Args[2:])
	case "run":
		err = runAll(os.Args[2:])
	case "inspect":
		err = runInspect(os.Args[2:])
	case "version":
		fmt.Println("tap 0.1.0")
	case "-h", "--help", "help":
		fmt.Println(usage)
	default:
		fmt.Fprintf(os.Stderr, "tap: unknown command %q\n\n%s\n", os.Args[1], usage)
		os.Exit(2)
	}
	if err != nil {
		fmt.Fprintf(os.Stderr, "tap: %v\n", err)
		os.Exit(1)
	}
}

func runNormalize(args []string) error {
	out := "normalized.jsonl"
	var inputs []string
	for i := 0; i < len(args); i++ {
		switch args[i] {
		case "-o", "--output":
			if i+1 >= len(args) {
				return fmt.Errorf("-o expects a path")
			}
			i++
			out = args[i]
		default:
			inputs = append(inputs, args[i])
		}
	}
	if len(inputs) == 0 {
		return fmt.Errorf("normalize needs a raw directory or file")
	}
	summaries, totalEvents, err := normalizeInto(inputs, out)
	if err != nil {
		return err
	}
	printNormalizeReport(summaries, totalEvents, out)
	return nil
}

// normalizeInto normalizes every tmon artifact under inputs and writes the
// non-excluded events to out. Returns per-run summaries and the event count.
func normalizeInto(inputs []string, out string) ([]model.ExecutionSummary, int, error) {
	files, err := jsonlFiles(inputs)
	if err != nil {
		return nil, 0, err
	}
	if len(files) == 0 {
		return nil, 0, fmt.Errorf("no .jsonl files found")
	}
	f, err := os.Create(out)
	if err != nil {
		return nil, 0, err
	}
	defer f.Close()
	w := bufio.NewWriter(f)
	defer w.Flush()
	enc := json.NewEncoder(w)

	var summaries []model.ExecutionSummary
	var totalEvents int
	for _, path := range files {
		events, sum, err := normalizeFile(path)
		if err != nil {
			return nil, 0, fmt.Errorf("%s: %w", path, err)
		}
		summaries = append(summaries, sum)
		if sum.Excluded {
			continue
		}
		for i := range events {
			if err := enc.Encode(&events[i]); err != nil {
				return nil, 0, err
			}
			totalEvents++
		}
	}
	return summaries, totalEvents, nil
}

func normalizeFile(path string) ([]model.Event, model.ExecutionSummary, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, model.ExecutionSummary{}, err
	}
	defer f.Close()
	ex, err := tmon.Parse(f)
	if err != nil {
		return nil, model.ExecutionSummary{}, err
	}
	return normalize.Normalize(ex)
}

func printNormalizeReport(summaries []model.ExecutionSummary, totalEvents int, out string) {
	configs := map[string]bool{}
	primitives := map[string]bool{}
	familyTotals := map[model.Family]int{}
	var excluded []model.ExecutionSummary
	for _, s := range summaries {
		configs[s.Config] = true
		primitives[s.Primitive] = true
		if s.Excluded {
			excluded = append(excluded, s)
			continue
		}
		for fam, n := range s.FamilyCounts {
			familyTotals[fam] += n
		}
	}
	fmt.Printf("tap normalize: %d executions · %d configs · %d primitives\n",
		len(summaries), len(configs), len(primitives))
	fmt.Printf("  %d normalized events → %s\n", totalEvents, out)

	fams := make([]string, 0, len(familyTotals))
	for fam := range familyTotals {
		fams = append(fams, string(fam))
	}
	sort.Strings(fams)
	parts := make([]string, 0, len(fams))
	for _, fam := range fams {
		parts = append(parts, fmt.Sprintf("%s=%d", fam, familyTotals[model.Family(fam)]))
	}
	if len(parts) > 0 {
		fmt.Printf("  by family: %s\n", strings.Join(parts, " "))
	}
	if len(excluded) > 0 {
		fmt.Printf("  excluded %d run(s):\n", len(excluded))
		for _, s := range excluded {
			fmt.Printf("    %s — %s\n", s.RunID, s.ExcludeReason)
		}
	}
}

func runInspect(args []string) error {
	if len(args) != 1 {
		return fmt.Errorf("inspect needs exactly one file")
	}
	events, sum, err := normalizeFile(args[0])
	if err != nil {
		return err
	}
	fmt.Printf("run:       %s\n", sum.RunID)
	fmt.Printf("config:    %s (os=%s language=%s compiler=%s runtime=%s)\n",
		sum.Config, sum.OS, sum.Language, sum.Compiler, sum.Runtime)
	fmt.Printf("primitive: %s   iteration: %d\n", sum.Primitive, sum.Iteration)
	fmt.Printf("events:    %d   target exit: %d   dropped: %d\n",
		len(events), sum.TargetExit, sum.Dropped)
	if sum.Excluded {
		fmt.Printf("EXCLUDED:  %s\n", sum.ExcludeReason)
	}
	fams := make([]string, 0, len(sum.FamilyCounts))
	for fam := range sum.FamilyCounts {
		fams = append(fams, string(fam))
	}
	sort.Strings(fams)
	for _, fam := range fams {
		fmt.Printf("  %-9s %d\n", fam, sum.FamilyCounts[model.Family(fam)])
	}
	return nil
}

// jsonlFiles expands inputs (files or directories) into a sorted list of .jsonl
// paths, so runs process in a deterministic order.
func jsonlFiles(inputs []string) ([]string, error) {
	var files []string
	for _, in := range inputs {
		info, err := os.Stat(in)
		if err != nil {
			return nil, err
		}
		if !info.IsDir() {
			files = append(files, in)
			continue
		}
		err = filepath.WalkDir(in, func(p string, d fs.DirEntry, err error) error {
			if err != nil {
				return err
			}
			if !d.IsDir() && strings.HasSuffix(p, ".jsonl") {
				files = append(files, p)
			}
			return nil
		})
		if err != nil {
			return nil, err
		}
	}
	sort.Strings(files)
	return files, nil
}
