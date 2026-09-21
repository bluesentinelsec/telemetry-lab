# The same image is used for all dynamically linked C, C++, and Go configurations.
FROM lab-substrate:13
RUN apt-get update && apt-get install -y --no-install-recommends iproute2 libstdc++6 \
    && rm -rf /var/lib/apt/lists/*
COPY linux-c-glibc /opt/coverage/linux-c-glibc
COPY linux-c-musl /opt/coverage/linux-c-musl
COPY helper /opt/coverage/helper
COPY linux-cpp-libstdcxx /opt/coverage/linux-cpp-libstdcxx
COPY linux-cpp-libcxx /opt/coverage/linux-cpp-libcxx
COPY linux-go-cgo /opt/coverage/linux-go-cgo
COPY linux-go-static /opt/coverage/linux-go-static
ENV TELEMETRY_LAB_FIXTURE=1
CMD ["sleep", "infinity"]
