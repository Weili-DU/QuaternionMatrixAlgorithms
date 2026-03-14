from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.experiments import run_reproduction


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Wang 2024 split quaternion SVD reproduction")
    parser.add_argument(
        "--config",
        type=str,
        default=str(ROOT / "configs" / "reproduce_config.json"),
        help="Path to reproduction config JSON",
    )
    args = parser.parse_args()
    config_path = Path(args.config).resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    summary = run_reproduction(ROOT, config)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
