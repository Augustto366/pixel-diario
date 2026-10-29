#!/usr/bin/env python3
"""Compatibilidade com o comando histórico ``python atualizar.py``."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from pixel_diario.cli import main


if __name__ == "__main__":
    main()
