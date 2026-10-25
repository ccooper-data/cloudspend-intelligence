#!/usr/bin/env bash
set -euo pipefail

project_id="${GCP_PROJECT_ID:-cloudspend-intelligence-v1}"
confirmation="${1:-}"

if [[ "${project_id}" != "cloudspend-intelligence-v1" ]]; then
  echo "Refusing to load outside the dedicated CloudSpend project." >&2
  exit 2
fi

if [[ "${confirmation}" != "LOAD_SYNTHETIC_DATA" ]]; then
  echo "Usage: $0 LOAD_SYNTHETIC_DATA" >&2
  exit 2
fi

for command_name in gcloud bq python3; do
  command -v "${command_name}" >/dev/null || {
    echo "Missing required command: ${command_name}" >&2
    exit 2
  }
done

active_project="$(gcloud config get-value project 2>/dev/null)"
if [[ "${active_project}" != "${project_id}" ]]; then
  echo "Active gcloud project is ${active_project}; expected ${project_id}." >&2
  exit 2
fi

echo "Loading 540 explicitly synthetic records into ${project_id}:cloudspend_v1.billing_records"
bq --location=US load \
  --replace \
  --source_format=CSV \
  --skip_leading_rows=1 \
  --schema=infra/schemas/billing_records.json \
  "${project_id}:cloudspend_v1.billing_records" \
  data/synthetic_gcp_billing.csv

python3 - "${project_id}" sql/detect_anomalies_bigquery.sql work/detect_anomalies_live.sql <<'PY'
from pathlib import Path
import sys

project_id, source, destination = sys.argv[1:]
rendered = Path(source).read_text(encoding="utf-8").replace("${project_id}", project_id)
Path(destination).parent.mkdir(exist_ok=True)
Path(destination).write_text(rendered, encoding="utf-8")
PY

bq --location=US query \
  --use_legacy_sql=false \
  --maximum_bytes_billed=10737418240 \
  < work/detect_anomalies_live.sql

python3 - "${project_id}" sql/validate_live.sql work/validate_live.sql <<'PY'
from pathlib import Path
import sys

project_id, source, destination = sys.argv[1:]
rendered = Path(source).read_text(encoding="utf-8").replace("${project_id}", project_id)
Path(destination).parent.mkdir(exist_ok=True)
Path(destination).write_text(rendered, encoding="utf-8")
PY

bq --location=US query \
  --use_legacy_sql=false \
  --maximum_bytes_billed=10737418240 \
  < work/validate_live.sql

echo "Live synthetic-data validation passed."
