FROM python:3.12 AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_SYSTEM_PYTHON=1


WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip wheel uv

COPY pyproject.toml uv.lock ./

RUN uv pip install -r pyproject.toml

COPY ./src/ /app/src/

EXPOSE 8000

FROM base AS dev
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
FROM base AS stage
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
FROM base AS prod
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]


FROM base AS test
RUN uv pip install -r pyproject.toml --group test
COPY tests/ /app/tests/
CMD ["pytest"]
