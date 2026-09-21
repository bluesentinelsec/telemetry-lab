package files

import (
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
	"os"
)

func Write(path string) {
	fixture.Must(os.WriteFile(path, []byte(fixture.Payload), 0600))
	st, err := os.Stat(path)
	fixture.Must(err)
	fixture.Check(st.Size() == int64(len(fixture.Payload)), "file size")
}
func Read(path string) {
	data, err := os.ReadFile(path)
	fixture.Must(err)
	fixture.Check(string(data) == fixture.Payload, "file contents")
}
func Truncate(path string) {
	f, err := os.OpenFile(path, os.O_WRONLY|os.O_TRUNC, 0)
	fixture.Must(err)
	fixture.Must(f.Close())
	st, err := os.Stat(path)
	fixture.Must(err)
	fixture.Check(st.Size() == 0, "truncate result")
}
