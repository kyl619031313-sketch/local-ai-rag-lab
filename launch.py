#!/usr/bin/env python3
"""Isolated local Open WebUI launcher; no changes to an existing WebUI database."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request

VERSION = "0.12.5"
ROOT = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser(description="启动本地 AI / RAG 学习实验")
    parser.add_argument("--model", default="qwen2.5:3b", help="首次下载的 Ollama 模型")
    parser.add_argument("--port", type=int, default=3016)
    parser.add_argument("--skip-pull", action="store_true", help="使用已经下载的模型，跳过下载")
    args = parser.parse_args()
    for binary in ("uv", "ollama"):
        if not shutil.which(binary):
            parser.exit(1, f"缺少 {binary}。请先按 README 安装并重新打开终端。\n")
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=5) as response:
            response.read()
    except Exception:
        parser.exit(1, "请先打开 Ollama 应用，或在另一个终端运行 ollama serve。\n")
    if not 1024 <= args.port <= 65535:
        parser.error("端口应在 1024 到 65535 之间")
    if not args.skip_pull:
        subprocess.run(["ollama", "pull", args.model], check=True)
    env = os.environ.copy()
    env.update({
        "DATA_DIR": str(ROOT / ".local-data"),
        "WEBUI_AUTH": "True",
        "OLLAMA_BASE_URL": "http://127.0.0.1:11434",
        "RAG_EMBEDDING_MODEL": "BAAI/bge-small-zh-v1.5",
        "SCARF_NO_ANALYTICS": "true",
        "DO_NOT_TRACK": "true",
        "ANONYMIZED_TELEMETRY": "false",
    })
    print(f"打开 http://127.0.0.1:{args.port} ，首次启动会下载依赖与嵌入模型。", flush=True)
    subprocess.run(["uv", "run", "--python", "3.11", "--with", f"open-webui=={VERSION}",
                    "open-webui", "serve", "--host", "127.0.0.1", "--port", str(args.port)],
                   env=env, check=True)

if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print("启动或下载失败，请保留上方错误，参考 docs/troubleshooting.md。", file=sys.stderr)
        sys.exit(exc.returncode)
    except KeyboardInterrupt:
        pass
