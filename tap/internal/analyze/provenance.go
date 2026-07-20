package analyze

import (
	"encoding/json"
	"os"
	"path/filepath"
)

// Provenance is the lab inventory (inventory.json) captured at provisioning time:
// the exact tool versions + SHA-256 hashes present on the host that produced the
// telemetry. When found co-located with the input data it is attached to Result,
// so every analysis artifact traces back to what generated it.
type Provenance struct {
	Generated           string                `json:"generated"`
	Host                string                `json:"host"`
	OS                  string                `json:"os"`
	Kernel              string                `json:"kernel,omitempty"`
	TelemetryLabRelease string                `json:"telemetry_lab_release"`
	Components          []ProvenanceComponent `json:"components"`
}

type ProvenanceComponent struct {
	Name    string `json:"name"`
	Type    string `json:"type"`
	Version string `json:"version"`
	SHA256  string `json:"sha256"`
	Path    string `json:"path"`
}

// LoadProvenance looks for inventory.json co-located with the given input path
// (which may be a file or a directory) and parses it. A missing file is not an
// error: it returns (nil, nil) so provenance is simply omitted from the output.
func LoadProvenance(inputPath string) (*Provenance, error) {
	dir := inputPath
	if fi, err := os.Stat(inputPath); err == nil && !fi.IsDir() {
		dir = filepath.Dir(inputPath)
	}
	b, err := os.ReadFile(filepath.Join(dir, "inventory.json"))
	if err != nil {
		if os.IsNotExist(err) {
			return nil, nil
		}
		return nil, err
	}
	var prov Provenance
	if err := json.Unmarshal(b, &prov); err != nil {
		return nil, err
	}
	return &prov, nil
}
