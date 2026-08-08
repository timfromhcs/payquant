FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    python3 \
    python3-pip \
    libssl-dev \
    libevent-dev \
    libboost-system-dev \
    libboost-filesystem-dev \
    libboost-test-dev \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages blake3 argon2-cffi qiskit pycryptodome

WORKDIR /payquant
COPY . .

# Ports: 28333 (Mainnet P2P), 28334 (Testnet P2P), 28335 (Regtest P2P), 28332 (RPC)
EXPOSE 28333 28334 28335 28332

CMD ["python3", "contrib/vulkan_miner.py"]
