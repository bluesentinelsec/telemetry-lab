//go:build windows

package files

import (
	"bytes"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"io"
	"os"
)

func CopyVerified(src, dst string) {
	in, err := os.Open(src)
	fixture.Must(err)
	out, err := os.OpenFile(dst, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0600)
	fixture.Must(err)
	buffer := make([]byte, 4096)
	for {
		n, e := in.Read(buffer)
		if n > 0 {
			written, err := out.Write(buffer[:n])
			fixture.Must(err)
			fixture.Check(written == n, "short file write")
		}
		if e == io.EOF {
			break
		}
		fixture.Must(e)
	}
	fixture.Must(out.Close())
	fixture.Must(in.Close())
	a, err := os.ReadFile(src)
	fixture.Must(err)
	b, err := os.ReadFile(dst)
	fixture.Must(err)
	fixture.Check(bytes.Equal(a, b), "file readback differs")
}
