from __future__ import annotations
import os
from pathlib import Path

_CONFIG = Path(__file__).resolve().parent
_LOCAL = _CONFIG / "local-paths.env"


def _load_local_env() -> None:
    if not _LOCAL.is_file():
        return
    for line in _LOCAL.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export ") :]
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        # Expand $VAR in values lightly
        val = os.path.expandvars(val)
        os.environ.setdefault(key, val)


_load_local_env()

HANGX_ROOT = Path(os.environ.get("HANGX_ROOT", str(Path.home() / "hangX")))
OMP_REPOS_ROOT = Path(os.environ.get("OMP_REPOS_ROOT", str(HANGX_ROOT / "repos")))
HANGX_JAIL_ROOT = Path(
    os.environ.get("HANGX_JAIL_ROOT", str(HANGX_ROOT / "vendor" / "jail" / "skills"))
)
SECLISTS_ROOT = Path(os.environ.get("SECLISTS_ROOT", str(Path.home() / "tools" / "SecLists")))
BURP_ROOT = Path(
    os.environ.get("BURP_ROOT", str(Path.home() / "tools" / "BurpSuiteCommunity"))
)
CERTIPY_BIN = Path(
    os.environ.get("CERTIPY_BIN", str(Path.home() / ".local" / "bin" / "certipy"))
)
NETEXEC_BIN = Path(
    os.environ.get("NETEXEC_BIN", str(Path.home() / ".local" / "bin" / "netexec"))
)
