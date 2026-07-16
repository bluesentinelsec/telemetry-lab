package model

// ExecutionSummary is one row per tmon run: its provenance, per-family event
// counts, and whether it was excluded from analysis (and why). The analyze stage
// groups these by (primitive, config); the report stage explains exclusions.
type ExecutionSummary struct {
	RunID     string `json:"run_id"`
	Config    string `json:"config"`
	Host      string `json:"host,omitempty"`
	OS        string `json:"os"`
	Language  string `json:"language"`
	Compiler  string `json:"compiler"`
	Runtime   string `json:"runtime"`
	Primitive string `json:"primitive"`
	Iteration int    `json:"iteration"`

	Events       int            `json:"events"`
	FamilyCounts map[Family]int `json:"family_counts"`
	Dropped      int64          `json:"dropped"`
	TargetExit   int            `json:"target_exit"`

	Excluded      bool   `json:"excluded"`
	ExcludeReason string `json:"exclude_reason,omitempty"`
}
