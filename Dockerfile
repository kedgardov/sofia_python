FROM python:3.13.2-slim-bookworm AS base

WORKDIR /app


#stage 1
FROM base AS builder
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    rustc \
    cargo \
    gfortran \
    pkg-config \
    libopenblas-dev \
    cmake \
 && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --upgrade  pip
RUN pip install --user -r requirements.txt


#Stage 2
FROM base
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

