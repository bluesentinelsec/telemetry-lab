// Package render draws the dissertation's figures from an analysis Result:
// per-primitive volume bar charts, baseline-attribution charts (behavior vs.
// runtime overhead), and within-OS Jaccard similarity heatmaps. Pure Go via
// gonum/plot, so it cross-compiles with the rest of tap.
package render

import (
	"fmt"
	"image/color"
	"os"
	"path/filepath"
	"sort"

	"gonum.org/v1/plot"
	"gonum.org/v1/plot/palette"
	"gonum.org/v1/plot/plotter"
	"gonum.org/v1/plot/vg"
	"gonum.org/v1/plot/vg/draw"

	"github.com/bluesentinelsec/telemetry-lab/tap/internal/analyze"
)

// Render writes all figures for the result into dir and returns their paths.
func Render(r analyze.Result, dir string) ([]string, error) {
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return nil, err
	}
	var files []string
	for _, p := range r.Primitives {
		for _, fn := range []func(analyze.PrimitiveResult, string) ([]string, error){
			volumeChart, baselineChart, jaccardHeatmaps,
		} {
			fs, err := fn(p, dir)
			if err != nil {
				return nil, err
			}
			files = append(files, fs...)
		}
	}
	return files, nil
}

func sortByTotal(cs []analyze.ConfigSummary) []analyze.ConfigSummary {
	out := append([]analyze.ConfigSummary(nil), cs...)
	sort.Slice(out, func(i, j int) bool {
		if out[i].TotalMedian != out[j].TotalMedian {
			return out[i].TotalMedian > out[j].TotalMedian
		}
		return out[i].Config < out[j].Config
	})
	return out
}

func rotateX(p *plot.Plot) {
	p.X.Tick.Label.Rotation = -0.6
	p.X.Tick.Label.XAlign = draw.XRight
	p.X.Tick.Label.YAlign = draw.YCenter
}

func volumeChart(pr analyze.PrimitiveResult, dir string) ([]string, error) {
	cfgs := sortByTotal(pr.Configs)
	if len(cfgs) == 0 {
		return nil, nil
	}
	vals := make(plotter.Values, len(cfgs))
	labels := make([]string, len(cfgs))
	for i, c := range cfgs {
		vals[i] = c.TotalMedian
		labels[i] = c.Config
	}
	p := plot.New()
	p.Title.Text = fmt.Sprintf("%s — total telemetry by config", pr.Primitive)
	p.Y.Label.Text = "median events / run"
	bars, err := plotter.NewBarChart(vals, vg.Points(24))
	if err != nil {
		return nil, err
	}
	bars.Color = color.RGBA{R: 70, G: 130, B: 180, A: 255}
	p.Add(bars)
	p.NominalX(labels...)
	rotateX(p)
	file := filepath.Join(dir, pr.Primitive+"_volume.png")
	return []string{file}, p.Save(8*vg.Inch, 4*vg.Inch, file)
}

func baselineChart(pr analyze.PrimitiveResult, dir string) ([]string, error) {
	var cfgs []analyze.ConfigSummary
	for _, c := range sortByTotal(pr.Configs) {
		if c.HasBaseline {
			cfgs = append(cfgs, c)
		}
	}
	if len(cfgs) == 0 {
		return nil, nil
	}
	behavior := make(plotter.Values, len(cfgs))
	overhead := make(plotter.Values, len(cfgs))
	labels := make([]string, len(cfgs))
	for i, c := range cfgs {
		b := c.BehaviorTotal
		if b < 0 {
			b = 0
		}
		behavior[i] = b
		overhead[i] = c.TotalMedian - b
		labels[i] = c.Config
	}
	p := plot.New()
	p.Title.Text = fmt.Sprintf("%s — behavior vs runtime overhead", pr.Primitive)
	p.Y.Label.Text = "median events / run"

	behBars, err := plotter.NewBarChart(behavior, vg.Points(24))
	if err != nil {
		return nil, err
	}
	behBars.Color = color.RGBA{R: 60, G: 160, B: 90, A: 255}
	ovBars, err := plotter.NewBarChart(overhead, vg.Points(24))
	if err != nil {
		return nil, err
	}
	ovBars.Color = color.RGBA{R: 200, G: 130, B: 60, A: 255}
	ovBars.StackOn(behBars)

	p.Add(behBars, ovBars)
	p.Legend.Add("behavior", behBars)
	p.Legend.Add("overhead", ovBars)
	p.Legend.Top = true
	p.NominalX(labels...)
	rotateX(p)
	file := filepath.Join(dir, pr.Primitive+"_baseline.png")
	return []string{file}, p.Save(8*vg.Inch, 4*vg.Inch, file)
}

// jaccardHeatmaps draws one heatmap per OS that has >= 2 configs.
func jaccardHeatmaps(pr analyze.PrimitiveResult, dir string) ([]string, error) {
	osByCfg := map[string]string{}
	for _, c := range pr.Configs {
		osByCfg[c.Config] = c.OS
	}
	// Group configs and pair-similarities by OS.
	cfgsByOS := map[string][]string{}
	seen := map[string]map[string]bool{}
	sim := map[string]float64{}
	key := func(a, b string) string {
		if a > b {
			a, b = b, a
		}
		return a + "|" + b
	}
	for _, j := range pr.Jaccard {
		os := osByCfg[j.ConfigA]
		if seen[os] == nil {
			seen[os] = map[string]bool{}
		}
		for _, c := range []string{j.ConfigA, j.ConfigB} {
			if !seen[os][c] {
				seen[os][c] = true
				cfgsByOS[os] = append(cfgsByOS[os], c)
			}
		}
		sim[key(j.ConfigA, j.ConfigB)] = j.Jaccard
	}

	var files []string
	for os, cfgs := range cfgsByOS {
		if len(cfgs) < 2 {
			continue
		}
		sort.Strings(cfgs)
		grid := jaccardGrid{configs: cfgs, sim: sim, key: key}
		pal := palette.Heat(12, 1)
		hm := plotter.NewHeatMap(grid, pal)
		p := plot.New()
		p.Title.Text = fmt.Sprintf("%s — syscall Jaccard similarity (%s)", pr.Primitive, os)
		p.Add(hm)
		p.NominalX(cfgs...)
		p.NominalY(cfgs...)
		rotateX(p)
		file := filepath.Join(dir, fmt.Sprintf("%s_jaccard_%s.png", pr.Primitive, os))
		if err := p.Save(6*vg.Inch, 5*vg.Inch, file); err != nil {
			return nil, err
		}
		files = append(files, file)
	}
	return files, nil
}

// jaccardGrid adapts the pairwise similarities to gonum's GridXYZ.
type jaccardGrid struct {
	configs []string
	sim     map[string]float64
	key     func(a, b string) string
}

func (g jaccardGrid) Dims() (int, int) { return len(g.configs), len(g.configs) }
func (g jaccardGrid) X(c int) float64  { return float64(c) }
func (g jaccardGrid) Y(r int) float64  { return float64(r) }
func (g jaccardGrid) Z(c, r int) float64 {
	if c == r {
		return 1
	}
	return g.sim[g.key(g.configs[c], g.configs[r])]
}
