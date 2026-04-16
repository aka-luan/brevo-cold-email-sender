# ProspectaAí - Sender Module

This module handles email campaign sending, follow-ups, and reporting for ProspectaAí.

## Features

- Send email campaigns to leads
- Automated follow-ups
- Weekly reporting
- Lead statistics and export

## Usage

### Send Campaign
```bash
python campaign.py send --limit 30
```

### Follow-up
```bash
python campaign.py followup
```

### Stats
```bash
python main.py stats
```

### Export Leads
```bash
python main.py export --output leads.csv
```

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Configure environment variables in `.env`
3. Run daily script: `./run_daily.sh` or `.\run_daily.ps1`