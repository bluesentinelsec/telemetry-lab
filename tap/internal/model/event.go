// Package model defines the common, normalized telemetry schema that tap emits
// from both eBPF (Linux) and ETW (Windows) tmon output. Every downstream stage
// (analyze, render, report) consumes this schema, so it is the contract that
// makes cross-runtime and cross-OS comparison possible.
package model

// Family is the telemetry family an event belongs to (dissertation "event_type").
// The families are the analysis axes; the user-mode-API family is deliberately
// out of scope (kernel-native instrumentation does not observe it).
type Family string

const (
	FamilySyscall  Family = "syscall"  // every system call (the full symbol set)
	FamilyProcess  Family = "process"  // process lifecycle: start/exec/exit
	FamilyFile     Family = "file"     // file I/O with a resolved path
	FamilyNetwork  Family = "network"  // socket/connect/send/recv with an endpoint
	FamilyLibrary  Family = "library"  // dynamic library / image load
	FamilyRegistry Family = "registry" // Windows registry key/value access
)

// Event is one normalized telemetry record. Provenance is denormalized onto
// every event so the artifact is self-describing and downstream grouping is a
// simple field match, matching the dissertation's per-execution artifact model.
type Event struct {
	// Provenance (from the tmon meta record + experiment controller).
	Host      string `json:"host,omitempty"`
	OS        string `json:"os"`        // "linux" | "windows"
	Language  string `json:"language"`  // c | cpp | go | rust
	Compiler  string `json:"compiler"`  // gcc | clang++ | ...
	Runtime   string `json:"runtime"`   // glibc | musl | libstdc++ | ...
	Primitive string `json:"primitive"` // spawn | connect | empty | ...
	Iteration int    `json:"iteration"`
	Config    string `json:"config"` // canonical id, e.g. "linux-c-glibc"
	RunID     string `json:"run_id"` // unique per (config, primitive, iteration)

	// Identity.
	TimeNs    int64  `json:"time_ns"` // nanoseconds since this run's first event
	PID       int    `json:"pid"`
	TID       int    `json:"tid,omitempty"`
	PPID      int    `json:"ppid,omitempty"`
	Comm      string `json:"comm,omitempty"`

	// Classification.
	Family Family `json:"family"`
	Name   string `json:"name"` // event_name: syscall name, "open", "connect", ...

	// Decoded, family-specific fields (dissertation "event_attributes").
	Attrs map[string]any `json:"attrs,omitempty"`
}
