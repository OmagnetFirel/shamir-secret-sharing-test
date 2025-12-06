FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    curl wget git ca-certificates \
    python3 python3-pip \
    openjdk-17-jdk maven \
    dotnet-sdk-8.0 \
    && rm -rf /var/lib/apt/lists/*

# Install modern Node.js (20.x) - Remove conflicting packages first
RUN apt-get update && \
    apt-get remove -y nodejs npm nodejs-doc libnode-dev 2>/dev/null || true && \
    apt-get autoremove -y && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy apenas arquivos de dependências PRIMEIRO (menos frequentes)
COPY java/ java/
COPY csharp/ csharp/
COPY python/requirements.txt python/
COPY js/package.json js/


# Python deps
RUN pip3 install -r python/requirements.txt

# JS deps
RUN cd js && npm install

# Java build
RUN cd java && mvn -q -DskipTests package

# C# build
RUN cd csharp/ShamirSecretSharing && dotnet restore && dotnet build -c Release
RUN cd csharp/TestSecretSharing && dotnet restore && dotnet build -c Release
RUN cd csharp/mtanksl && dotnet restore && dotnet build -c Release

# Copy SCRIPTS no final (muda com frequência)
COPY python/*.py python/
COPY js/*.js js/
COPY java/src/ java/src/
COPY orchestrator.py libs_config.json ./

CMD ["python3", "orchestrator.py"]