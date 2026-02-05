FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN python -m pip install --upgrade pip && pip install -e ".[dev]"

ENV AETHER_LLM=stub
ENV AETHER_TRACE_DIR=/app/traces
ENV AETHER_WORKSPACE=/app/workspace

CMD ["aether", "chat"]
