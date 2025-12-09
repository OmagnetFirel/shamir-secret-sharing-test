FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    curl wget git ca-certificates \
    python3 python3-pip python3-venv \
    openjdk-17-jdk maven \
    dotnet-sdk-8.0 \
    && rm -rf /var/lib/apt/lists/*

# Install modern Node.js (20.x)
RUN apt-get update && \
    apt-get remove -y nodejs npm nodejs-doc libnode-dev 2>/dev/null || true && \
    apt-get autoremove -y && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy apenas arquivos de dependências PRIMEIRO
COPY java/ java/
COPY csharp/ csharp/
COPY python/ python/
COPY js/package.json js/

# Cria venv para cada subpasta Python e instala dependências isoladamente
RUN for dir in /app/python/*/; do \
        if [ -f "$dir/requirements.txt" ]; then \
            venv_name=$(basename "$dir"); \
            echo "Creating venv for $venv_name"; \
            python3 -m venv "$dir/.venv"; \
            "$dir/.venv/bin/pip" install --upgrade pip; \
            "$dir/.venv/bin/pip" install -r "$dir/requirements.txt"; \
        fi \
    done

# JS deps
RUN cd js && npm install

# Java build
RUN cd java && mvn -q -DskipTests package

# C# build
RUN cd csharp/ShamirSecretSharing && dotnet restore && dotnet build -c Release
RUN cd csharp/TestSecretSharing && dotnet restore && dotnet build -c Release
RUN cd csharp/mtanksl && dotnet restore && dotnet build -c Release

# Copy SCRIPTS no final
COPY python/*.py python/
COPY js/*.js js/
COPY java/src/ java/src/
COPY orchestrator.py libs_config.json ./

CMD ["python3", "orchestrator.py"]
