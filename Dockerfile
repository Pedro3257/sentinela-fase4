FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY sentinela ./sentinela
RUN python -m pip install --no-cache-dir .
WORKDIR /data
ENTRYPOINT ["python", "-m", "sentinela"]
CMD ["demo", "--out", "/data/demo"]
