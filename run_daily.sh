#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

mkdir -p logs
LOG_FILE="logs/cron.log"

DRY_RUN_FLAG=""
if [[ "${PROSPECTAAI_DRY_RUN:-0}" = "1" ]]; then
  DRY_RUN_FLAG="--dry-run"
fi

{
  python campaign.py send --limit 30 ${DRY_RUN_FLAG}
  python campaign.py followup ${DRY_RUN_FLAG}
} >> "${LOG_FILE}" 2>&1
