FROM mambaorg/micromamba:1.5-jammy
WORKDIR /app
COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml pyproject.toml ./
COPY --chown=$MAMBA_USER:$MAMBA_USER src ./src
RUN micromamba install -y -n base -f environment.yml && micromamba clean -a -y
COPY --chown=$MAMBA_USER:$MAMBA_USER . .
ARG MAMBA_DOCKERFILE_ACTIVATE=1
CMD ["make", "all"]
