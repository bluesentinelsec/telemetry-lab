# Constant substrate base image for container detonation of ttp_composites.
#
# It is debian:13 (matching the EC2 host's major version) plus EVERY runtime the
# dynamically-linked substrates need: the musl loader (linux-c-musl), the LLVM
# C++ runtime (linux-cpp-libcxx), and tmon's runtime deps. glibc is already in
# the base. Statically-linked substrates (go-static, rust-*) need nothing extra.
#
# One image, all runtimes, held CONSTANT across the whole substrate matrix — so
# the container is a fixed offset, not a per-substrate variable. This is the
# load-bearing confound control for Option A (see issue #39, Section A).
FROM debian:13

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      musl libc++1 libc++abi1 libunwind8 \
      libelf1 zlib1g libzstd1 \
      ca-certificates \
 && rm -rf /var/lib/apt/lists/*
