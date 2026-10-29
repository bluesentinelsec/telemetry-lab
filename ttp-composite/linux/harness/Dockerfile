# The same image is used for all eight C, C++, Go, and Rust configurations.
FROM lab-substrate:13
RUN apt-get update && apt-get install -y --no-install-recommends iproute2 libstdc++6 grep coreutils dpkg util-linux python3 ncat openssh-client openssh-server curl rsync e2fsprogs docker.io docker-cli apache2 unzip \
    && rm -rf /var/lib/apt/lists/*
# Pin a real package manager explicitly listed by the unchanged npm-ancestry rule.
RUN curl -fsSL https://github.com/oven-sh/bun/releases/download/bun-v1.3.0/bun-linux-x64-baseline.zip -o /tmp/bun.zip \
    && printf '%s  /tmp/bun.zip\n' '77336611905b9e876e52924f8b1a57e72669cf10541dc1e11269d2c9371f9e45' | sha256sum -c - \
    && unzip -q /tmp/bun.zip -d /tmp/bun \
    && install -m 0755 /tmp/bun/bun-linux-x64-baseline/bun /usr/local/bin/bun \
    && rm -rf /tmp/bun /tmp/bun.zip
RUN useradd --uid 2000 --no-create-home --shell /bin/sh labfixture
COPY fixtures /opt/lab-fixtures
ENV PYTHONDONTWRITEBYTECODE=1
COPY linux-c-glibc /opt/coverage/linux-c-glibc
COPY linux-c-musl /opt/coverage/linux-c-musl
COPY helper /opt/coverage/helper
COPY linux-cpp-libstdcxx /opt/coverage/linux-cpp-libstdcxx
COPY linux-cpp-libcxx /opt/coverage/linux-cpp-libcxx
COPY linux-go-cgo /opt/coverage/linux-go-cgo
COPY linux-go-static /opt/coverage/linux-go-static
COPY linux-rust-gnu /opt/coverage/linux-rust-gnu
COPY linux-rust-musl /opt/coverage/linux-rust-musl
ENV TELEMETRY_LAB_FIXTURE=1
CMD ["sleep", "infinity"]
