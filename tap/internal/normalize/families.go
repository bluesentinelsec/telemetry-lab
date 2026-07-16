package normalize

import (
	"fmt"
	"strings"

	"github.com/bluesentinelsec/telemetry-lab/tap/internal/model"
	"github.com/bluesentinelsec/telemetry-lab/tap/internal/tmon"
)

// normalizeLinux maps one Linux tmon event to normalized events. Every syscall
// becomes a `syscall`-family event; path/socket-bearing syscalls additionally
// synthesize the semantic family event, mirroring Windows' first-class streams.
func normalizeLinux(ev tmon.Record, ts int64, emit func(model.Event)) {
	base := model.Event{TimeNs: ts, PID: ev.PID, TID: ev.TID, Comm: ev.Comm}
	switch ev.Kind {
	case "fork":
		e := base
		e.Family, e.Name = model.FamilyProcess, "fork"
		e.Attrs = map[string]any{"child_pid": ev.ChildPID}
		emit(e)
	case "exec":
		e := base
		e.Family, e.Name = model.FamilyProcess, "exec"
		emit(e)
	case "exit":
		e := base
		e.Family, e.Name = model.FamilyProcess, "exit"
		if ev.ExitCode != nil {
			e.Attrs = map[string]any{"exit_code": *ev.ExitCode}
		}
		emit(e)
	case "syscall":
		name := ev.Syscall
		if name == "" && ev.Nr != nil {
			name = fmt.Sprintf("syscall_%d", *ev.Nr)
		}
		// (1) the raw syscall.
		sc := base
		sc.Family, sc.Name = model.FamilySyscall, name
		sc.Attrs = syscallAttrs(ev)
		emit(sc)
		// (2) derived semantic event, if any.
		if d, ok := deriveLinux(base, name, ev); ok {
			emit(d)
		}
	}
}

func syscallAttrs(ev tmon.Record) map[string]any {
	a := map[string]any{}
	if ev.Ret != nil {
		a["ret"] = *ev.Ret
	}
	if ev.OK != nil {
		a["ok"] = *ev.OK
	}
	if ev.Error != "" {
		a["error"] = ev.Error
	}
	if ev.DurationNs != nil {
		a["duration_ns"] = *ev.DurationNs
	}
	if len(a) == 0 {
		return nil
	}
	return a
}

// deriveLinux synthesizes a file/network/library event from a decoded syscall.
func deriveLinux(base model.Event, name string, ev tmon.Record) (model.Event, bool) {
	// Network: identified by syscall name; carries the decoded sockaddr if any.
	if op, ok := networkOps[name]; ok {
		e := base
		e.Family, e.Name = model.FamilyNetwork, op
		if ev.Sockaddr != "" {
			e.Attrs = map[string]any{"remote": ev.Sockaddr}
		}
		return e, true
	}
	// Path-bearing syscalls become library loads (shared objects) or file ops.
	if ev.Path != "" {
		e := base
		if isSharedObject(ev.Path) && (name == "openat" || name == "open" || name == "mmap") {
			e.Family, e.Name = model.FamilyLibrary, "load"
			e.Attrs = map[string]any{"path": ev.Path}
			return e, true
		}
		if op, ok := fileOps[name]; ok {
			e.Family, e.Name = model.FamilyFile, op
			e.Attrs = map[string]any{"path": ev.Path}
			if ev.Ret != nil {
				e.Attrs["ret"] = *ev.Ret
			}
			return e, true
		}
	}
	return model.Event{}, false
}

// normalizeWindows maps one Windows tmon event; its families are already
// first-class, so this is a direct translation.
func normalizeWindows(ev tmon.Record, ts int64, emit func(model.Event)) {
	base := model.Event{TimeNs: ts, PID: ev.PID, TID: ev.TID}
	switch ev.Kind {
	case "syscall":
		e := base
		e.Family = model.FamilySyscall
		if ev.Syscall != "" {
			e.Name = ev.Syscall
		} else {
			e.Name = ev.SyscallAddress
		}
		emit(e)
	case "process_start":
		e := base
		e.Family, e.Name, e.PPID = model.FamilyProcess, "start", ev.PPID
		e.Attrs = nonEmpty(map[string]any{"image": ev.Image})
		emit(e)
	case "process_stop":
		e := base
		e.Family, e.Name = model.FamilyProcess, "stop"
		e.Attrs = nonEmpty(map[string]any{"image": ev.Image, "exit_code": ev.ExitCode})
		emit(e)
	case "image":
		e := base
		e.Family, e.Name = model.FamilyLibrary, "load"
		e.Attrs = nonEmpty(map[string]any{"path": ev.Image})
		emit(e)
	case "file":
		e := base
		e.Family, e.Name = model.FamilyFile, ev.Op
		e.Attrs = fileNetAttrs(ev)
		emit(e)
	case "network":
		e := base
		e.Family, e.Name = model.FamilyNetwork, ev.Op
		e.Attrs = fileNetAttrs(ev)
		emit(e)
	case "registry":
		e := base
		e.Family, e.Name = model.FamilyRegistry, ev.Op
		e.Attrs = nonEmpty(map[string]any{"key": ev.Key, "value": ev.Value})
		emit(e)
	}
}

func fileNetAttrs(ev tmon.Record) map[string]any {
	a := map[string]any{
		"path": ev.Path, "protocol": ev.Protocol,
		"local": ev.Local, "remote": ev.Remote,
	}
	if ev.Size != nil {
		a["size"] = *ev.Size
	}
	return nonEmpty(a)
}

func nonEmpty(a map[string]any) map[string]any {
	for k, v := range a {
		switch x := v.(type) {
		case string:
			if x == "" {
				delete(a, k)
			}
		case *int:
			if x == nil {
				delete(a, k)
			} else {
				a[k] = *x
			}
		}
	}
	if len(a) == 0 {
		return nil
	}
	return a
}

func isSharedObject(path string) bool {
	return strings.HasSuffix(path, ".so") || strings.Contains(path, ".so.")
}

// networkOps maps Linux network syscalls to a normalized operation name aligned
// with the Windows network op vocabulary where possible.
var networkOps = map[string]string{
	"socket": "socket", "connect": "connect", "bind": "bind", "listen": "listen",
	"accept": "accept", "accept4": "accept", "sendto": "send", "recvfrom": "recv",
	"sendmsg": "send", "recvmsg": "recv", "getsockname": "getsockname",
	"getpeername": "getpeername", "setsockopt": "setsockopt",
	"getsockopt": "getsockopt", "shutdown": "shutdown",
}

// fileOps maps path-bearing Linux syscalls to a normalized file operation name.
var fileOps = map[string]string{
	"open": "open", "openat": "open", "openat2": "open", "creat": "create",
	"stat": "stat", "lstat": "stat", "newfstatat": "stat", "statx": "stat",
	"access": "access", "faccessat": "access", "faccessat2": "access",
	"unlink": "unlink", "unlinkat": "unlink", "rename": "rename",
	"renameat": "rename", "renameat2": "rename", "mkdir": "mkdir",
	"mkdirat": "mkdir", "rmdir": "rmdir", "chmod": "chmod", "fchmodat": "chmod",
	"chown": "chown", "readlink": "readlink", "readlinkat": "readlink",
	"statfs": "statfs", "truncate": "truncate", "chdir": "chdir",
	"getxattr": "getxattr", "lgetxattr": "getxattr", "mknod": "mknod",
}
