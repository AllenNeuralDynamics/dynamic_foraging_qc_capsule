# hash:sha256:561c9309b904e308dadfa982b44d5b645296d956e35031dcd06b61cc95040eb9
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgl1=1.4.0-1 \
        libglib2.0-0=2.72.4-0ubuntu2.10 \
        libxcb1=1.14-3ubuntu3 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -U --no-cache-dir \
    log-schema==0.2.10.dev1 \
    watchtower==3.4.0

COPY postInstall /
RUN --mount=type=secret,id=secrets . /run/secrets/secrets \
    && /postInstall
