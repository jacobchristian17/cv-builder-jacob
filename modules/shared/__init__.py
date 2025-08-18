"""
Shared Resources Module

This module contains shared resources:
- Data files (personal_info.json)
- Configuration files
- Common utilities
- Shared constants
"""

import json
import os
from pathlib import Path

def load_personal_data(filename="personal_info.json"):
    """Load personal data from JSON file."""
    data_path = Path(__file__).parent / "data" / filename
    
    if not data_path.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")
    
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)

__all__ = ['load_personal_data']