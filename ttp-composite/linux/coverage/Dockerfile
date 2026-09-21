# The same image is used for both dynamically linked C configurations.
FROM lab-substrate:13
RUN apt-get update && apt-get install -y --no-install-recommends iproute2 \
    && rm -rf /var/lib/apt/lists/*
COPY linux-c-glibc /opt/coverage/linux-c-glibc
COPY linux-c-musl /opt/coverage/linux-c-musl
COPY helper /opt/coverage/helper
ENV TELEMETRY_LAB_FIXTURE=1
CMD ["sleep", "infinity"]
