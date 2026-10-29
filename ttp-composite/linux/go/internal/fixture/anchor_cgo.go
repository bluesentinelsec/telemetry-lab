//go:build cgo

package fixture

// Match the existing Go primitive axis: explicitly link runtime/cgo so that
// even file-only and baseline programs have a real cgo/static distinction.
// No C function performs the tested behavior. This is a linkage/startup
// configuration, not a claim that CGO_ENABLED changes every Go library API.

/*
#include <stddef.h>
*/
import "C"

var _ = C.size_t(0)
