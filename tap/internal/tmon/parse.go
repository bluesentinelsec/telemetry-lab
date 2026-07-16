// Package tmon parses the raw JSONL that the tmon monitors emit. It handles both
// dialects (Linux/eBPF and Windows/ETW) into a single Execution the normalizer
// can consume. It does not interpret telemetry semantics -- that is normalize's
// job -- it only decodes the wire records.
package tmon

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io"
)

// Record is the union of fields across both tmon dialects. A record is a "meta",
// "event", or "summary" line; only the fields relevant to that record/kind and
// platform are populated.
type Record struct {
	Record string `json:"record"` // meta | event | summary

	// --- meta ---
	Tool    string            `json:"tool"`
	OS      string            `json:"os"` // Windows sets this; Linux omits it
	Command []string          `json:"command"`
	Meta    map[string]string `json:"meta"`

	// --- event: common ---
	Kind string `json:"kind"`
	PID  int    `json:"pid"`
	TID  int    `json:"tid"`
	Comm string `json:"comm"` // Linux acting-task name

	// --- event: Linux syscall ---
	TsNs       *int64   `json:"ts_ns"`
	Nr         *int64   `json:"nr"`
	Syscall    string   `json:"syscall"`
	Args       []string `json:"args"`
	Path       string   `json:"path"`
	Sockaddr   string   `json:"sockaddr"`
	Ret        *int64   `json:"ret"`
	OK         *bool    `json:"ok"`
	Error      string   `json:"error"`
	Errno      *int     `json:"errno"`
	DurationNs *int64   `json:"duration_ns"`
	ChildPID   int      `json:"child_pid"`
	ExitCode   *int     `json:"exit_code"`

	// --- event: Windows ---
	TimeMsec       *float64 `json:"time_msec"`
	SyscallAddress string   `json:"syscall_address"`
	Op             string   `json:"op"`
	Size           *int64   `json:"size"`
	Offset         *int64   `json:"offset"`
	Protocol       string   `json:"protocol"`
	Local          string   `json:"local"`
	Remote         string   `json:"remote"`
	Key            string   `json:"key"`
	Value          string   `json:"value"`
	Image          string   `json:"image"`
	PPID           int      `json:"ppid"`

	// --- summary ---
	SyscallEvents  int64  `json:"syscall_events"`
	FailedSyscalls int64  `json:"failed_syscalls"`
	TotalEvents    int64  `json:"total_events"`
	Processes      int    `json:"processes"`
	Dropped        *int64 `json:"dropped"` // Linux
	Lost           *int64 `json:"lost"`    // Windows
	TargetExitCode int    `json:"target_exit_code"`
}

// Execution is one parsed tmon run (one JSONL file).
type Execution struct {
	OS         string   // detected: "linux" | "windows"
	Command    []string // argv of the traced target
	Meta       map[string]string
	Events     []Record
	Summary    Record
	HasSummary bool
}

// Parse reads one tmon JSONL stream into an Execution. Unknown or malformed
// lines return an error identifying the line, so bad data fails loudly rather
// than silently skewing analysis.
func Parse(r io.Reader) (*Execution, error) {
	sc := bufio.NewScanner(r)
	sc.Buffer(make([]byte, 0, 1024*1024), 16*1024*1024) // large records (paths)

	ex := &Execution{}
	line := 0
	for sc.Scan() {
		line++
		b := sc.Bytes()
		if len(b) == 0 {
			continue
		}
		var rec Record
		if err := json.Unmarshal(b, &rec); err != nil {
			return nil, fmt.Errorf("line %d: %w", line, err)
		}
		switch rec.Record {
		case "meta":
			ex.Command = rec.Command
			ex.Meta = rec.Meta
			ex.OS = detectOS(rec)
		case "event":
			ex.Events = append(ex.Events, rec)
		case "summary":
			ex.Summary = rec
			ex.HasSummary = true
		default:
			return nil, fmt.Errorf("line %d: unknown record %q", line, rec.Record)
		}
	}
	if err := sc.Err(); err != nil {
		return nil, err
	}
	if ex.OS == "" {
		ex.OS = detectOSFromEvents(ex.Events)
	}
	return ex, nil
}

// detectOS uses the meta record: Windows tmon stamps os:windows; the experiment
// controller may also pass os via --meta. Linux omits it.
func detectOS(meta Record) string {
	if meta.OS != "" {
		return meta.OS
	}
	if meta.Meta != nil {
		if v := meta.Meta["os"]; v != "" {
			return v
		}
	}
	return ""
}

// detectOSFromEvents is the fallback: Linux events carry ts_ns; Windows events
// carry time_msec.
func detectOSFromEvents(events []Record) string {
	for _, e := range events {
		if e.TsNs != nil {
			return "linux"
		}
		if e.TimeMsec != nil {
			return "windows"
		}
	}
	return "linux"
}

// Dropped returns the count of events lost to buffer pressure (Linux "dropped",
// Windows "lost"), and whether the run reported completeness at all.
func (e *Execution) Dropped() (int64, bool) {
	if !e.HasSummary {
		return 0, false
	}
	if e.Summary.Dropped != nil {
		return *e.Summary.Dropped, true
	}
	if e.Summary.Lost != nil {
		return *e.Summary.Lost, true
	}
	return 0, true
}
