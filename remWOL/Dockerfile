FROM python:3.12-slim

LABEL org.opencontainers.image.title="Wake-on-LAN API Server"
LABEL org.opencontainers.image.description="HTTP API server to send WOL magic packets"
LABEL org.opencontainers.image.source="https://github.com/maggicone/remWOL-moonlight"
LABEL org.opencontainers.image.licenses="MIT"

ENV WOL_PORT=8765 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY server.py .

EXPOSE 8765

HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=10s \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8765/health')"

CMD ["python3", "server.py"]
