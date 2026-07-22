#!/usr/bin/env bash
# Fire matrix: detonate every composite under every substrate config in a
# container and record which shipped Falco rule fires. Run ON the Debian lab
# host (has bash, docker, falco). Filters harness noise (the -v bind mount fires
# "Launch Sensitive Mount Container" on every run; "BPF Program Not Profiled" is
# Falco internal noise) -- neither is part of the technique under test.
IMG=lab-substrate:13
V=/opt/lab/compdist
COMPS="reverse_shell imds read_sensitive_file symlink_sensitive clear_log mkdir_bin ptrace_antidebug"
CFGS="linux-c-glibc linux-c-musl linux-cpp-libstdcxx linux-cpp-libcxx linux-go-cgo linux-go-static linux-rust-gnu linux-rust-musl"
NOISE='Launch Sensitive Mount Container|BPF Program Not Profiled'

printf "%-20s  Cg Cm Xs Xc Gc Gs Rg Rm   | primary rule\n" "composite"
printf -- "-------------------------------------------------------------------\n"
for comp in $COMPS; do
  row=""; rule=""
  for cfg in $CFGS; do
    t0=$(date '+%Y-%m-%d %H:%M:%S')
    timeout 15 docker run --rm -v "$V":/comp:ro "$IMG" /comp/$cfg/$comp >/dev/null 2>&1
    sleep 2
    r=$(journalctl -u falco-modern-bpf.service --since "$t0" -o cat --no-pager 2>/dev/null \
        | grep -oE '"rule":"[^"]*"' | sed 's/.*rule...//;s/.$//' | grep -vE "$NOISE" | sort -u)
    if [ -n "$r" ]; then row="$row  F"; [ -z "$rule" ] && rule=$(echo "$r" | head -1); else row="$row  ."; fi
  done
  printf "%-20s %s   | %s\n" "$comp" "$row" "${rule:-<none = EVADE>}"
done
