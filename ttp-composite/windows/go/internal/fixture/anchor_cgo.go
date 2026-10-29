//go:build cgo

package fixture

// Match the existing Go primitive axis: explicitly link runtime/cgo so that
// even file-only and baseline programs have a real cgo/pure-Go distinction.
// No C function performs the tested behavior. This is a linkage/startup
// configuration; the measured actions remain in Go and Windows bindings.
// In particular, this does not force Windows DNS resolution through a C API.

/*
#include <stddef.h>
*/
import "C"

var _ = C.size_t(0)
