# hash:sha256:610fb64be15318ef62bf94cc6b5010d5c98555bbdd577d4fc48f1616ab9f7447
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgl1=1.4.0-1 \
        libglib2.0-0=2.72.4-0ubuntu2.9 \
        libxcb1=1.14-3ubuntu3 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -U --no-cache-dir \
    log-schema==0.2.10.dev1 \
    watchtower==3.4.0

COPY postInstall /
RUN --mount=type=secret,id=secrets . /run/secrets/secrets \
    && /postInstall
