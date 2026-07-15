# PoC build: libbpf CO-RE. Requires clang, libbpf-dev, bpftool, and a kernel
# with BTF (/sys/kernel/btf/vmlinux). vmlinux.h and the BPF skeleton are
# generated, not committed.

CLANG   ?= clang
BPFTOOL ?= bpftool
ARCH    := $(shell uname -m | sed 's/x86_64/x86/;s/aarch64/arm64/')

.PHONY: all clean
all: monitor spawner

vmlinux.h:
	$(BPFTOOL) btf dump file /sys/kernel/btf/vmlinux format c > vmlinux.h

monitor.bpf.o: monitor.bpf.c vmlinux.h
	$(CLANG) -O2 -g -target bpf -D__TARGET_ARCH_$(ARCH) -I. -c monitor.bpf.c -o monitor.bpf.o

monitor.skel.h: monitor.bpf.o
	$(BPFTOOL) gen skeleton monitor.bpf.o > monitor.skel.h

monitor: monitor.c monitor.skel.h
	$(CLANG) -O2 -I. monitor.c -o monitor -lbpf -lelf -lz

spawner: spawner.c
	$(CC) -O2 spawner.c -o spawner

clean:
	rm -f monitor spawner *.o *.skel.h vmlinux.h
