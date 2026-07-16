// Package normalize turns a parsed tmon Execution (either dialect) into the
// common schema. The central job is reconciling the two monitors: Windows emits
// first-class file/network/registry/image events, while Linux is syscall-centric
// with decoded paths/sockaddrs. The normalizer keeps every syscall as the
// `syscall` family AND synthesizes the semantic family events (file/network/
// library/process) from the decoded Linux syscalls, so both platforms present
// one comparable per-family model.
package normalize

import (
	"fmt"
	"strconv"
	"strings"

	"github.com/bluesentinelsec/telemetry-lab/tap/internal/model"
	"github.com/bluesentinelsec/telemetry-lab/tap/internal/tmon"
)

// Normalize converts one execution into normalized events plus a summary row.
// The summary is always returned (even when excluded) so exclusions are
// auditable; when Excluded is true the event slice is still produced but callers
// typically drop it from analysis.
func Normalize(ex *tmon.Execution) ([]model.Event, model.ExecutionSummary, error) {
	p := provenance(ex)
	sum := model.ExecutionSummary{
		RunID: p.runID(), Config: p.config(), Host: p.host, OS: p.os,
		Language: p.language, Compiler: p.compiler, Runtime: p.runtime,
		Primitive: p.primitive, Iteration: p.iteration,
		FamilyCounts: map[model.Family]int{},
	}

	if ex.HasSummary {
		sum.TargetExit = ex.Summary.TargetExitCode
	}
	if dropped, ok := ex.Dropped(); ok {
		sum.Dropped = dropped
	}
	// Exclusion policy: a run must have finished (summary present) and be
	// complete (no dropped/lost events) to enter analysis.
	switch {
	case !ex.HasSummary:
		sum.Excluded, sum.ExcludeReason = true, "no summary (run did not complete)"
	case sum.Dropped > 0:
		sum.Excluded = true
		sum.ExcludeReason = fmt.Sprintf("%d dropped events (incomplete telemetry)", sum.Dropped)
	}

	base := int64(-1) // first event's timestamp, for rebasing to 0
	var out []model.Event
	emit := func(e model.Event) {
		applyProvenance(&e, p)
		out = append(out, e)
		sum.FamilyCounts[e.Family]++
	}

	for _, ev := range ex.Events {
		ts := eventTimeNs(ex.OS, ev)
		if base < 0 || ts < base {
			base = ts
		}
	}
	for _, ev := range ex.Events {
		ts := eventTimeNs(ex.OS, ev) - base
		if ex.OS == "windows" {
			normalizeWindows(ev, ts, emit)
		} else {
			normalizeLinux(ev, ts, emit)
		}
	}

	sum.Events = len(out)
	return out, sum, nil
}

func eventTimeNs(os string, ev tmon.Record) int64 {
	if os == "windows" {
		if ev.TimeMsec != nil {
			return int64(*ev.TimeMsec * 1e6)
		}
		return 0
	}
	if ev.TsNs != nil {
		return int64(*ev.TsNs)
	}
	return 0
}

// --- provenance ---

type prov struct {
	host, os, language, compiler, runtime, primitive, configOverride string
	iteration                                                        int
}

func provenance(ex *tmon.Execution) prov {
	m := ex.Meta
	get := func(k string) string {
		if m == nil {
			return ""
		}
		return m[k]
	}
	p := prov{
		host: get("host"), os: ex.OS, language: get("language"),
		compiler: get("compiler"), runtime: get("runtime"),
		primitive: get("primitive"), configOverride: get("config"),
	}
	if p.os == "" {
		p.os = get("os")
	}
	p.iteration, _ = strconv.Atoi(get("iteration"))
	return p
}

func (p prov) config() string {
	if p.configOverride != "" {
		return p.configOverride
	}
	parts := []string{p.os, p.language, p.runtime}
	var nonEmpty []string
	for _, s := range parts {
		if s != "" {
			nonEmpty = append(nonEmpty, s)
		}
	}
	return strings.Join(nonEmpty, "-")
}

func (p prov) runID() string {
	return fmt.Sprintf("%s/%s/%d", p.config(), p.primitive, p.iteration)
}

func applyProvenance(e *model.Event, p prov) {
	e.Host, e.OS, e.Language, e.Compiler = p.host, p.os, p.language, p.compiler
	e.Runtime, e.Primitive, e.Iteration = p.runtime, p.primitive, p.iteration
	e.Config, e.RunID = p.config(), p.runID()
}
