FROM mambaorg/micromamba:2.0-debian12-slim
WORKDIR /app
COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml pyproject.toml README.md ./
COPY --chown=$MAMBA_USER:$MAMBA_USER src ./src
RUN micromamba install -y -n base -f environment.yml && micromamba clean -a -y
COPY --chown=$MAMBA_USER:$MAMBA_USER . .
ARG MAMBA_DOCKERFILE_ACTIVATE=1
ENV MPLBACKEND=Agg
# data/raw is mounted, never baked into the image
CMD ["make", "all"]
