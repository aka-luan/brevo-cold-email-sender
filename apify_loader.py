import csv
import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def load_apify_csv(filepath: str) -> list[dict[str, Any]]:
    """
    Load and validate leads from an Apify CSV export.
    
    Args:
        filepath: Path to the CSV file
        
    Returns:
        List of validated lead dicts with Apify CSV headers as keys
        
    Logs:
        - Number of rows loaded
        - Number of rows skipped (invalid email or missing required fields)
    """
    csv_path = Path(filepath)
    
    if not csv_path.exists():
        logger.warning(f"CSV file not found: {filepath}")
        return []
    
    leads = []
    skipped = 0
    total = 0
    
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            
            if reader.fieldnames is None:
                logger.error("CSV file is empty or has no headers")
                return []
            
            for row in reader:
                total += 1
                
                # Strip whitespace from all values
                cleaned_row = {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
                
                # Validate email
                email = cleaned_row.get("email", "").strip()
                if not email or not _is_valid_email(email):
                    logger.debug(f"Skipping row {total}: invalid or missing email '{email}'")
                    skipped += 1
                    continue
                
                leads.append(cleaned_row)
    
    except Exception as e:
        logger.error(f"Error reading CSV file '{filepath}': {e}")
        return []
    
    logger.info(f"Loaded {len(leads)} rows from {filepath} ({skipped} skipped)")
    return leads


def _is_valid_email(email: str) -> bool:
    """
    Simple email validation using regex.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email matches pattern \S+@\S+\.\S+
    """
    pattern = r"\S+@\S+\.\S+"
    return bool(re.match(pattern, email))
