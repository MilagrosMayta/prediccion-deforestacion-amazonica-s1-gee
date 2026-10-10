from __future__ import annotations

import shutil


def detectar_gpt() -> str | None:
    return shutil.which("gpt") or shutil.which("gpt.exe")
