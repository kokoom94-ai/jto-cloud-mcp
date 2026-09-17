FROM rust:1.95-bookworm AS auto_builder
WORKDIR /build
RUN git clone --filter=blob:none https://github.com/kwakseongjae/auto-hwp.git . && git checkout d96d1f2f40458dc3d4470392524dcda9e43ac304 && git submodule update --init --recursive --depth 1
RUN cargo build --locked --release -j 2 -p auto-hwp-cli --features rhwp,shaper,pdf

FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends hunspell hunspell-ko fonts-nanum ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=auto_builder /build/target/release/auto-hwp /usr/local/bin/auto-hwp
COPY --from=auto_builder /build/LICENSE /usr/share/doc/auto-hwp/LICENSE
COPY --from=auto_builder /build/NOTICE /usr/share/doc/auto-hwp/NOTICE
COPY --from=auto_builder /build/assets/fonts/ /build/assets/fonts/
WORKDIR /app
COPY pyproject.toml .
COPY jto_cloud ./jto_cloud
RUN pip install --no-cache-dir . && useradd -m -u 10001 jto && mkdir /data && chown jto:jto /data
USER jto
ENV JTO_DATA_DIR=/data PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["jto-cloud-mcp"]
