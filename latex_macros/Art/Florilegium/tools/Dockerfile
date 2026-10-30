# TeX Live 2023 (Ubuntu 24.04) for building florilegium without a local TeX install:
#   docker build -t florilegium-tex tools && make RUN=tools/in-docker
FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-luatex texlive-latex-recommended texlive-latex-extra texlive-pictures \
    texlive-fonts-recommended lmodern cm-super make poppler-utils python3 python3-pil \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /work
