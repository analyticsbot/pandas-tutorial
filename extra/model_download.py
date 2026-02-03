from huggingface_hub import hf_hub_download
from pathlib import Path

# Download local GGUF from community repo
local_gguf = hf_hub_download(
    repo_id="lmstudio-community/Qwen3-VL-30B-A3B-Instruct-GGUF",  # community GGUF repo
    filename="Qwen3-VL-30B-A3B-Instruct-Q4_K_M.gguf",                # quant file
    local_dir=str(Path("./models/qwen3vl30b").resolve()),           # where to save
    cache_dir=str(Path("./models/qwen3vl30b").resolve())            # ensure local caching
)

print("GGUF downloaded to:", local_gguf)
