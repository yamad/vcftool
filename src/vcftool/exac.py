"""ExAC (Exome Aggregation Consortium) API support"""
import json
from collections import Sequence

import requests
import logging

logger = logging.getLogger(__name__)

def fetch_bulk_variant(variant_ids: Sequence[str]):
    """Fetch variant data for multiple variants from ExAC /bulk/variant endpoint"""
    res = requests.post("http://exac.hms.harvard.edu/rest/bulk/variant",
                 data = json.dumps(variant_ids), timeout=2)

    res.raise_for_status()
    return res.json()

def fetch_variant(variant_id):
    res = requests.get(f"http://exac.hms.harvard.edu/rest/variant/{variant_id}", timeout=2)
    res.raise_for_status()
    return res.json()