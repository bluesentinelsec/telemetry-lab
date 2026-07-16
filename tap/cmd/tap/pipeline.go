package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"

	"github.com/bluesentinelsec/telemetry-lab/tap/internal/analyze"
	"github.com/bluesentinelsec/telemetry-lab/tap/internal/render"
	"github.com/bluesentinelsec/telemetry-lab/tap/internal/report"
)

func loadResult(path string) (analyze.Result, error) {
	f, err := os.Open(path)
	if err != nil {
		return analyze.Result{}, err
	}
	defer f.Close()
	var r analyze.Result
	if err := json.NewDecoder(f).Decode(&r); err != nil {
		return analyze.Result{}, err
	}
	return r, nil
}

func runRender(args []string) error {
	out := "figures"
	var input string
	for i := 0; i < len(args); i++ {
		if args[i] == "-o" || args[i] == "--output" {
			if i+1 >= len(args) {
				return fmt.Errorf("-o expects a path")
			}
			i++
			out = args[i]
		} else {
			input = args[i]
		}
	}
	if input == "" {
		return fmt.Errorf("render needs an analysis.json input")
	}
	r, err := loadResult(input)
	if err != nil {
		return err
	}
	files, err := render.Render(r, out)
	if err != nil {
		return err
	}
	fmt.Printf("tap render: %d figures → %s/\n", len(files), out)
	return nil
}

func runReport(args []string) error {
	out := "report.md"
	var input string
	for i := 0; i < len(args); i++ {
		if args[i] == "-o" || args[i] == "--output" {
			if i+1 >= len(args) {
				return fmt.Errorf("-o expects a path")
			}
			i++
			out = args[i]
		} else {
			input = args[i]
		}
	}
	if input == "" {
		return fmt.Errorf("report needs an analysis.json input")
	}
	r, err := loadResult(input)
	if err != nil {
		return err
	}
	if err := os.WriteFile(out, []byte(report.Render(r)), 0o644); err != nil {
		return err
	}
	fmt.Printf("tap report: %s\n", out)
	return nil
}

// runAll executes the whole pipeline: normalize -> analyze -> render -> report.
func runAll(args []string) error {
	var dir string
	var input string
	for i := 0; i < len(args); i++ {
		if args[i] == "-o" || args[i] == "--output" {
			if i+1 >= len(args) {
				return fmt.Errorf("-o expects a results dir")
			}
			i++
			dir = args[i]
		} else {
			input = args[i]
		}
	}
	if input == "" || dir == "" {
		return fmt.Errorf("run needs a raw input and -o <results-dir>")
	}
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return err
	}

	// Stage 1: normalize into <dir>/normalized.jsonl.
	normPath := filepath.Join(dir, "normalized.jsonl")
	if _, _, err := normalizeInto([]string{input}, normPath); err != nil {
		return err
	}

	// Stage 2: analyze.
	nf, err := os.Open(normPath)
	if err != nil {
		return err
	}
	profiles, err := analyze.Load(nf)
	nf.Close()
	if err != nil {
		return err
	}
	result := analyze.Analyze(profiles)
	analysisPath := filepath.Join(dir, "analysis.json")
	if err := writeJSON(analysisPath, &result); err != nil {
		return err
	}

	// Stage 3 + 4: render + report.
	figs, err := render.Render(result, filepath.Join(dir, "figures"))
	if err != nil {
		return err
	}
	reportPath := filepath.Join(dir, "report.md")
	if err := os.WriteFile(reportPath, []byte(report.Render(result)), 0o644); err != nil {
		return err
	}

	fmt.Printf("tap run → %s\n", dir)
	fmt.Printf("  normalized.jsonl · analysis.json · %d figures · report.md\n", len(figs))
	return nil
}

func writeJSON(path string, v any) error {
	f, err := os.Create(path)
	if err != nil {
		return err
	}
	defer f.Close()
	w := bufio.NewWriter(f)
	enc := json.NewEncoder(w)
	enc.SetIndent("", "  ")
	if err := enc.Encode(v); err != nil {
		return err
	}
	return w.Flush()
}
