FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
COPY jto_cloud ./jto_cloud
RUN pip install --no-cache-dir . && useradd -m -u 10001 jto && mkdir /data && chown jto:jto /data
USER jto
ENV JTO_DATA_DIR=/data PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["jto-cloud-mcp"]
