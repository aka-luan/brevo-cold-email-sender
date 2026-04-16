#!/usr/bin/env python
"""Test script to verify apify_loader.py functionality."""

import logging
import os
import sys

# Setup logging to see the loader's output
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

# Add parent dir to path so we can import apify_loader
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from apify_loader import load_apify_csv


def mask_email(email: str) -> str:
    """Mask email for display: j***@domain.com"""
    if "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        masked_local = local[0:1] + "*"
    else:
        masked_local = local[:2] + "***"
    return f"{masked_local}@{domain}"


def test_csv_loader():
    """Test the CSV loader with test_apify.csv"""
    print("=" * 60)
    print("Testing Apify CSV Loader")
    print("=" * 60)
    
    csv_path = os.path.join(os.path.dirname(__file__), "test_apify.csv")
    leads = load_apify_csv(csv_path)
    
    print(f"\nLoaded {len(leads)} valid rows:\n")
    
    for i, lead in enumerate(leads, 1):
        masked = mask_email(lead.get("email", ""))
        title = lead.get("title", "N/A")
        keyword = lead.get("keyword", "N/A")
        nicho = lead.get("nicho", lead.get("keyword", "comercio"))  # Show normalized nicho
        url = lead.get("url", "N/A")
        description = lead.get("description", "")[:50] + "..." if len(lead.get("description", "")) > 50 else lead.get("description", "N/A")
        
        print(f"Row {i}:")
        print(f"  Email (masked):  {masked}")
        print(f"  Title:           {title}")
        print(f"  Keyword/Nicho:   {keyword} → nicho={nicho}")
        print(f"  URL:             {url}")
        print(f"  Description:     {description}")
        print()


if __name__ == "__main__":
    test_csv_loader()
