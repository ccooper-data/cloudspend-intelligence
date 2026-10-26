"""Render the reviewable Cloud Workflow template without cloud access."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def render(project_id: str) -> str:
    if not project_id or any(char not in "abcdefghijklmnopqrstuvwxyz0123456789-" for char in project_id):
        raise ValueError("project_id must contain only lowercase letters, digits, and hyphens")

    query = (ROOT / "sql" / "detect_anomalies_bigquery.sql").read_text(encoding="utf-8")
    query = query.replace("${project_id}", project_id)
    template = (ROOT / "infra" / "workflow.yaml.tftpl").read_text(encoding="utf-8")
    return (
        template.replace("${project_id}", project_id)
        .replace("${detector_query_json}", json.dumps(query))
        .replace("$${", "${")
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.write_text(render(args.project), encoding="utf-8")


if __name__ == "__main__":
    main()
