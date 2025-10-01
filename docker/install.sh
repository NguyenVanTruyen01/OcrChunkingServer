# Install make
apt update && apt install -y make && apt clean && rm -rf /var/lib/apt/lists/*

# Install uv
pip install --no-cache-dir uv==0.7.12

# Install dependencies using uv
uv pip sync --system --compile-bytecode uv.lock