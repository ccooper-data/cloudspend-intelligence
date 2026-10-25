from __future__ import annotations

import argparse
import json
from pathlib import Path

from .detector import connect, detect, load_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect anomalies in synthetic GCP-style billing data")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("reports/anomalies.json"))
    args = parser.parse_args()
    db = connect()
    load_csv(db, args.input)
    anomalies = detect(db)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps([a.to_dict() for a in anomalies], indent=2) + "\n", encoding="utf-8")
    for anomaly in anomalies:
        print(anomaly.explanation)
    print(f"Wrote {len(anomalies)} anomaly records to {args.output}")


if __name__ == "__main__":
    main()

