from pathlib import Path
import json
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.experiments import run_scan, save_outputs


def main() -> None:
    config_path = PROJECT_ROOT / "configs" / "reproduce.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Missing config file: {config_path}")
    df = run_scan(config_path)
    out = save_outputs(df, PROJECT_ROOT / "outputs")
    summary_json = PROJECT_ROOT / "outputs" / "logs" / "summary.json"
    with summary_json.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "rows": len(df),
                "trend_ok": bool(out["trend_ok"]),
                "table": out["table"],
                "figure": out["figure"],
                "log": out["log"],
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(df.to_string(index=False))
    print("\nSaved:")
    print(f"- {out['table']}")
    print(f"- {out['figure']}")
    print(f"- {out['log']}")
    print(f"- {summary_json}")


if __name__ == "__main__":
    main()
