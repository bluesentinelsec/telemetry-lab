//go:build windows

package regops

import (
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"golang.org/x/sys/windows/registry"
)

func SetRegistry(path, name, value string) {
	key, err := registry.OpenKey(registry.CURRENT_USER, path, registry.SET_VALUE|registry.QUERY_VALUE)
	fixture.Must(err)
	fixture.Must(key.SetStringValue(name, value))
	actual, kind, err := key.GetStringValue(name)
	fixture.Must(err)
	fixture.Check(kind == registry.SZ && actual == value, "registry readback differs")
	fixture.Must(key.Close())
}

func SetDword(path, name string, value uint32) {
	key, err := registry.OpenKey(registry.CURRENT_USER, path, registry.SET_VALUE|registry.QUERY_VALUE)
	fixture.Must(err)
	fixture.Must(key.SetDWordValue(name, value))
	actual, kind, err := key.GetIntegerValue(name)
	fixture.Must(err)
	fixture.Check(kind == registry.DWORD && actual == uint64(value), "registry DWORD readback differs")
	fixture.Must(key.Close())
}
