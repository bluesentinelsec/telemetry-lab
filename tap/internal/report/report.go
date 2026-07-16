// Package report turns an analysis Result into a Markdown findings document
// organized by the dissertation's research questions. It is the bridge from
// processed data to the answers the study is after; the numbers come straight
// from analyze.
package report

import (
	"fmt"
	"sort"
	"strings"

	"github.com/bluesentinelsec/telemetry-lab/tap/internal/analyze"
)

// Render produces the by-RQ Markdown report.
func Render(r analyze.Result) string {
	var b strings.Builder
	b.WriteString("# Telemetry analysis — findings by research question\n\n")
	b.WriteString(fmt.Sprintf("Primitives analyzed: %d\n\n", len(r.Primitives)))

	rq1(&b, r)
	rq2(&b, r)
	rq3(&b, r)
	rq4(&b, r)
	return b.String()
}

// RQ1 — telemetry differences within each family under different configs.
func rq1(b *strings.Builder, r analyze.Result) {
	b.WriteString("## RQ1 — Telemetry differences within each family\n\n")
	for _, p := range r.Primitives {
		b.WriteString(fmt.Sprintf("### %s\n\n", p.Primitive))
		b.WriteString("| config | total | syscall | file | network | library | process |\n")
		b.WriteString("|---|--:|--:|--:|--:|--:|--:|\n")
		cfgs := sortByTotalDesc(p.Configs)
		for _, c := range cfgs {
			b.WriteString(fmt.Sprintf("| %s | %.0f | %s | %s | %s | %s | %s |\n",
				c.Config, c.TotalMedian,
				fam(c, "syscall"), fam(c, "file"), fam(c, "network"),
				fam(c, "library"), fam(c, "process")))
		}
		if len(p.Jaccard) > 0 {
			hi, lo := extremaJaccard(p.Jaccard)
			b.WriteString(fmt.Sprintf("\nSyscall symbol overlap (Jaccard): most similar %s↔%s = %.2f; most divergent %s↔%s = %.2f.\n\n",
				hi.ConfigA, hi.ConfigB, hi.Jaccard, lo.ConfigA, lo.ConfigB, lo.Jaccard))
		} else {
			b.WriteString("\n")
		}
	}
}

// RQ2 — how much telemetry is runtime init/teardown vs. behavior (baseline).
func rq2(b *strings.Builder, r analyze.Result) {
	b.WriteString("## RQ2 — Runtime initialization/teardown attribution\n\n")
	b.WriteString("Behavior-attributable telemetry is the primitive's total minus the `empty` control's total for the same config; the rest is runtime overhead.\n\n")
	for _, p := range r.Primitives {
		if p.Primitive == "empty" {
			continue
		}
		var rows []string
		for _, c := range sortByTotalDesc(p.Configs) {
			if !c.HasBaseline {
				continue
			}
			overhead := 0.0
			if c.TotalMedian > 0 {
				overhead = 100 * (c.TotalMedian - c.BehaviorTotal) / c.TotalMedian
			}
			rows = append(rows, fmt.Sprintf("| %s | %.0f | %.0f | %.0f%% |\n",
				c.Config, c.TotalMedian, c.BehaviorTotal, overhead))
		}
		if len(rows) == 0 {
			continue
		}
		b.WriteString(fmt.Sprintf("### %s\n\n", p.Primitive))
		b.WriteString("| config | total | behavior | runtime overhead |\n|---|--:|--:|--:|\n")
		for _, row := range rows {
			b.WriteString(row)
		}
		b.WriteString("\n")
	}
}

// RQ3 — cross-OS differences (Debian vs Windows) and platform-specific artifacts.
func rq3(b *strings.Builder, r analyze.Result) {
	b.WriteString("## RQ3 — Cross-OS differences (Debian vs Windows)\n\n")
	b.WriteString("Compared at the semantic-family layer, since raw syscall names are not comparable across OSes.\n\n")
	any := false
	for _, p := range r.Primitives {
		if len(p.CrossOS) == 0 {
			continue
		}
		any = true
		b.WriteString(fmt.Sprintf("### %s\n\n", p.Primitive))
		b.WriteString("| family | Linux | Windows | shared ops | Linux-only | Windows-only |\n|---|--:|--:|---|---|---|\n")
		for _, f := range p.CrossOS {
			b.WriteString(fmt.Sprintf("| %s | %.0f | %.0f | %s | %s | %s |\n",
				f.Family, f.LinuxMedian, f.WindowsMedian,
				join(f.Shared), join(f.LinuxOnly), join(f.WindowsOnly)))
		}
		b.WriteString("\n")
	}
	if !any {
		b.WriteString("_No primitive had both Linux and Windows data in this run._\n\n")
	}
}

// RQ4 — stable (invariant) vs implementation-dependent (substrate) features.
func rq4(b *strings.Builder, r analyze.Result) {
	b.WriteString("## RQ4 — Stable vs implementation-dependent characteristics\n\n")
	for _, p := range r.Primitives {
		b.WriteString(fmt.Sprintf("### %s\n\n", p.Primitive))
		oses := make([]string, 0, len(p.StableByOS))
		for os := range p.StableByOS {
			oses = append(oses, os)
		}
		sort.Strings(oses)
		for _, os := range oses {
			stable := p.StableByOS[os]
			b.WriteString(fmt.Sprintf("- **Stable across all %s configs** (%d candidate invariants): %s\n",
				os, len(stable), join(head(stable, 12))))
		}
		if len(p.SubstrateSpecific) > 0 {
			b.WriteString("- **Substrate-specific** (avoid in detections):\n")
			for _, u := range p.SubstrateSpecific {
				b.WriteString(fmt.Sprintf("  - `%s`: %s\n", u.Config, join(head(u.Syscalls, 8))))
			}
		}
		b.WriteString("\n")
	}
}

// --- helpers ---

func fam(c analyze.ConfigSummary, name string) string {
	if v, ok := c.FamilyMedian[name]; ok {
		return fmt.Sprintf("%.0f", v)
	}
	return "0"
}

func sortByTotalDesc(cs []analyze.ConfigSummary) []analyze.ConfigSummary {
	out := append([]analyze.ConfigSummary(nil), cs...)
	sort.Slice(out, func(i, j int) bool {
		if out[i].TotalMedian != out[j].TotalMedian {
			return out[i].TotalMedian > out[j].TotalMedian
		}
		return out[i].Config < out[j].Config
	})
	return out
}

func extremaJaccard(ps []analyze.Pair) (hi, lo analyze.Pair) {
	hi, lo = ps[0], ps[0]
	for _, p := range ps {
		if p.Jaccard > hi.Jaccard {
			hi = p
		}
		if p.Jaccard < lo.Jaccard {
			lo = p
		}
	}
	return
}

func head(s []string, n int) []string {
	if len(s) <= n {
		return s
	}
	return append(s[:n:n], fmt.Sprintf("… (+%d)", len(s)-n))
}

func join(s []string) string {
	if len(s) == 0 {
		return "—"
	}
	return strings.Join(s, ", ")
}
