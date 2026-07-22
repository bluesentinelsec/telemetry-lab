//go:build linux

package main

// thread_create primitive: start one worker goroutine and wait for it.
//
// The C reference creates one pthread and joins it, exercising the kernel's
// clone/thread telemetry path (a new task sharing the address space, as opposed
// to spawn's separate process). The worker does nothing; the point is the
// create/join lifecycle, not the work.
//
// DOCUMENTED NUANCE (Go equivalent): a goroutine is NOT a 1:1 analogue of a
// pthread. The Go runtime multiplexes many goroutines onto a small pool of OS
// threads (the M:N scheduler), so starting one goroutine may issue no clone at
// all -- the runtime often already has an idle OS thread to run it on, and it
// may reuse a thread rather than clone a fresh one. This is the honest Go
// equivalent of "create one worker and join it": it exercises the goroutine
// create/wait lifecycle, but the observable clone telemetry can differ from the
// pthread case. The cgo/static substrate split lives in anchor_cgo.go.
//
// Linux-only for this pass (portable via std::thread on Windows -- issue #44).

import (
	"sync"
)

func main() {
	var wg sync.WaitGroup
	wg.Add(1)
	go func() {
		// no-op worker; the lifecycle is the signal, not the work
		defer wg.Done()
	}()
	wg.Wait()
}
