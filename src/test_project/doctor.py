"""C.A.W.L. Doctor — automated diagnostics and repair."""

from __future__ import annotations

import importlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / ".cawl-data"
SETTINGS_FILE = DATA_DIR / "settings.json"

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, msg: str = ""):
    status = f"{GREEN}OK{RESET}" if ok else f"{RED}FAIL{RESET}"
    results.append((name, ok, msg))
    print(f"  [{status}] {name}" + (f" — {msg}" if msg and not ok else ""))


def fix(name: str, msg: str):
    print(f"  {YELLOW}FIX{RESET} {name} — {msg}")


# ---------------------------------------------------------------------------
# Python
# ---------------------------------------------------------------------------

def check_python():
    print(f"\n{BOLD}Python{RESET}")
    v = sys.version_info
    check("Python version", v >= (3, 11), f"{v.major}.{v.minor}.{v.micro}")

    mods = [("fastapi", "fastapi"), ("uvicorn", "uvicorn"), ("httpx", "httpx"),
            ("pydantic", "pydantic"), ("pydub", "pydub"), ("edge_tts", "edge-tts"),
            ("yaml", "pyyaml")]
    for mod, pip_name in mods:
        try:
            importlib.import_module(mod)
            check(f"Module: {pip_name}", True)
        except ImportError:
            check(f"Module: {pip_name}", False, f"pip install {pip_name}")


# ---------------------------------------------------------------------------
# uv
# ---------------------------------------------------------------------------

def check_uv():
    print(f"\n{BOLD}uv{RESET}")
    uv = shutil.which("uv")
    check("uv on PATH", uv is not None, "" if uv else "install: pip install uv")
    if uv:
        try:
            r = subprocess.run([uv, "--version"], capture_output=True, text=True, timeout=5)
            check("uv version", True, r.stdout.strip())
        except Exception:
            check("uv version", False, "could not run uv --version")


# ---------------------------------------------------------------------------
# Node / npm / Electron
# ---------------------------------------------------------------------------

def check_node():
    print(f"\n{BOLD}Node.js / Electron{RESET}")
    node = shutil.which("node")
    npm = shutil.which("npm")
    check("node on PATH", node is not None)
    check("npm on PATH", npm is not None)

    electron_dir = PROJECT_ROOT / "node_modules" / "electron"
    check("Electron installed", electron_dir.exists(), "" if electron_dir.exists() else "run: npm install")

    pkg = PROJECT_ROOT / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
            check("package.json valid", True, f"v{data.get('version', '?')}")
        except Exception:
            check("package.json valid", False, "corrupt JSON")
    else:
        check("package.json", False, "missing")


# ---------------------------------------------------------------------------
# ffmpeg / yt-dlp
# ---------------------------------------------------------------------------

def check_media():
    print(f"\n{BOLD}Media Tools (/watch skill){RESET}")

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        # Check imageio-ffmpeg bundled binary
        try:
            import imageio_ffmpeg
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
            ffmpeg = ffmpeg and Path(ffmpeg).exists()
        except ImportError:
            ffmpeg = None
    if not ffmpeg:
        # Check local bins
        for bin_path in [PROJECT_ROOT / "bin" / "ffmpeg.exe",
                         Path.home() / "bin" / "ffmpeg.exe"]:
            if bin_path.exists():
                ffmpeg = str(bin_path)
                break
    check("ffmpeg", bool(ffmpeg), "" if ffmpeg else "install: winget install Gyan.FFmpeg")

    ytdlp = shutil.which("yt-dlp")
    check("yt-dlp", ytdlp is not None, "" if ytdlp else "pip install yt-dlp")


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

def check_server():
    print(f"\n{BOLD}Server{RESET}")
    import httpx

    try:
        resp = httpx.get("http://127.0.0.1:8123/self", timeout=3)
        data = resp.json()
        check("Server running", True, f"provider: {data.get('provider', '?')}")
        check("Brain online", data.get("brain_online", False))
    except Exception:
        check("Server running", False, "not responding on port 8123")


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

def check_settings():
    print(f"\n{BOLD}Settings{RESET}")

    if SETTINGS_FILE.exists():
        try:
            data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            check("settings.json valid", True)
        except Exception:
            check("settings.json valid", False, "corrupt JSON — will reset")
            data = {}
    else:
        check("settings.json", False, "will create")
        data = {}

    # API keys
    key_checks = {
        "OPENROUTER_API_KEY": "OpenRouter",
        "GROQ_API_KEY": "Groq",
        "MISTRAL_API_KEY": "Mistral",
        "GEMINI_API_KEY": "Gemini",
        "NVIDIA_API_KEY": "NVIDIA NIM",
        "WWV_API_KEY": "WorldWideView",
    }
    any_key = False
    for env_key, label in key_checks.items():
        val = os.getenv(env_key) or data.get(env_key, "")
        if val:
            any_key = True
            check(f"Key: {label}", True)
        else:
            check(f"Key: {label}", False, "not set (optional)")

    if not any_key:
        print(f"  {YELLOW}NOTE{RESET} No API keys configured. Brain will use offline/echo mode.")


# ---------------------------------------------------------------------------
# Ports
# ---------------------------------------------------------------------------

def check_ports():
    print(f"\n{BOLD}Ports{RESET}")
    import socket

    for port, name in [(8123, "CAWL"), (3000, "WorldWideView"), (5000, "WWV Data Engine")]:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(("127.0.0.1", port))
        sock.close()
        check(f"Port {port} ({name})", result == 0, "in use" if result == 0 else "free")


# ---------------------------------------------------------------------------
# WorldWideView
# ---------------------------------------------------------------------------

def check_wwv():
    print(f"\n{BOLD}WorldWideView{RESET}")
    wwv_dir = Path(r"C:\Users\Kristian\worldwideview")
    check("WWV directory", wwv_dir.exists(), "" if wwv_dir.exists() else "not found")

    if wwv_dir.exists():
        node_modules = wwv_dir / "node_modules"
        check("WWV dependencies", node_modules.exists(), "" if node_modules.exists() else "run: cd wwv && pnpm install")

    try:
        import httpx
        resp = httpx.get("http://localhost:3000/api/health", timeout=3)
        check("WWV running", resp.status_code == 200)
    except Exception:
        check("WWV running", False, "not responding on port 3000")


# ---------------------------------------------------------------------------
# Vault / Identity
# ---------------------------------------------------------------------------

def check_vault():
    print(f"\n{BOLD}Vault / Identity{RESET}")
    vault = PROJECT_ROOT / "vault"
    check("Vault directory", vault.exists())

    identity = vault / "01 Identity"
    check("Identity folder", identity.exists())

    for name in ["Persona.md", "Vow.md"]:
        p = identity / name
        check(f"Identity/{name}", p.exists())

    user_ctx = vault / "02 Memory" / "User Context.md"
    check("User Context.md", user_ctx.exists())

    index = vault / "Index.md"
    check("vault/Index.md", index.exists())


# ---------------------------------------------------------------------------
# Git
# ---------------------------------------------------------------------------

def check_git():
    print(f"\n{BOLD}Git{RESET}")
    git_dir = PROJECT_ROOT / ".git"
    check("Git repo", git_dir.exists())

    if git_dir.exists():
        try:
            r = subprocess.run(
                ["git", "remote", "-v"],
                capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=5
            )
            has_remote = "origin" in r.stdout
            check("Remote configured", has_remote, "" if has_remote else "run: git remote add origin <url>")
        except Exception:
            check("Remote configured", False, "git not available")


# ---------------------------------------------------------------------------
# Auto-fix
# ---------------------------------------------------------------------------

def auto_fix():
    print(f"\n{BOLD}Auto-Fix{RESET}")
    fixed = 0

    # Ensure data dirs exist
    for d in [DATA_DIR, DATA_DIR / "audio", DATA_DIR / "img", DATA_DIR / "logs"]:
        if not d.exists():
            d.mkdir(parents=True, exist_ok=True)
            fix("Create directory", str(d))
            fixed += 1

    # Ensure settings.json exists
    if not SETTINGS_FILE.exists():
        SETTINGS_FILE.write_text("{}\n", encoding="utf-8")
        fix("Create settings.json", "empty settings file")
        fixed += 1

    # Ensure token exists
    token_file = PROJECT_ROOT / ".cawl-token"
    if not token_file.exists():
        import secrets
        token = secrets.token_urlsafe(32)
        token_file.write_text(token + "\n", encoding="utf-8")
        fix("Generate auth token", str(token_file))
        fixed += 1

    # Ensure bin dir exists
    bin_dir = Path.home() / "bin"
    if not bin_dir.exists():
        bin_dir.mkdir(parents=True, exist_ok=True)
        fix("Create ~/bin", "for cawl.bat")
        fixed += 1

    # Copy cawl.bat to ~/bin if missing or outdated
    bat_src = PROJECT_ROOT / "cawl.bat"
    bat_dst = bin_dir / "cawl.bat"
    if bat_src.exists():
        src_content = bat_src.read_text(encoding="utf-8")
        dst_content = bat_dst.read_text(encoding="utf-8") if bat_dst.exists() else ""
        if src_content != dst_content:
            shutil.copy2(bat_src, bat_dst)
            fix("Update cawl.bat", str(bat_dst))
            fixed += 1

    if fixed == 0:
        print(f"  {GREEN}Nothing to fix{RESET}")
    else:
        print(f"  {GREEN}{fixed} fix(es) applied{RESET}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run():
    print(f"\n{'='*60}")
    print(f"  {BOLD}C.A.W.L. DOCTOR{RESET} — Diagnostic Report")
    print(f"{'='*60}")

    check_python()
    check_uv()
    check_node()
    check_media()
    check_settings()
    check_vault()
    check_git()
    check_wwv()
    check_ports()
    check_server()

    # Auto-fix
    auto_fix()

    # Summary
    passed = sum(1 for _, ok, _ in results if ok)
    failed = sum(1 for _, ok, _ in results if not ok)
    total = len(results)

    print(f"\n{'='*60}")
    if failed == 0:
        print(f"  {GREEN}ALL {total} CHECKS PASSED{RESET} — The Machine Spirit is whole.")
    else:
        print(f"  {passed}/{total} passed, {RED}{failed} failed{RESET}")
        print(f"\n  {BOLD}Failed checks:{RESET}")
        for name, ok, msg in results:
            if not ok:
                print(f"    {RED}x{RESET} {name}" + (f" — {msg}" if msg else ""))
    print(f"{'='*60}\n")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run())
