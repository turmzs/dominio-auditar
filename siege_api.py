import os
import requests
from typing import List, Dict, Any

# Base URL for Siege API – adjust if needed
SIEG_BASE_URL = os.getenv('SIEG_BASE_URL', 'https://api.sieg.com')
# API key – expected to be set in environment variable SIEG_API_KEY
SIEG_API_KEY = os.getenv('SIEG_API_KEY')

if not SIEG_API_KEY:
    print("AVISO: A variável de ambiente SIEG_API_KEY não está configurada. A sincronização automática da API Sieg estará desabilitada.")

def _auth_headers() -> Dict[str, str]:
    """Return authentication headers required by the Sieg API."""
    if not SIEG_API_KEY:
        raise ValueError("Chave de API Sieg (SIEG_API_KEY) não está configurada no ambiente local.")
    return {
        'Authorization': f'Bearer {SIEG_API_KEY}',
        'Accept': 'application/json',
    }

def list_invoices(cnpj: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """Fetch a list of invoices for a given company (CNPJ) between dates.

    Args:
        cnpj: Company CNPJ (numeric string).
        start_date: ISO date string 'YYYY-MM-DD'.
        end_date: ISO date string 'YYYY-MM-DD'.

    Returns:
        A list of dictionaries, each representing an invoice returned by the API.
    """
    endpoint = f"{SIEG_BASE_URL}/invoices"
    params = {
        'cnpj': cnpj,
        'start_date': start_date,
        'end_date': end_date,
    }
    response = requests.get(endpoint, headers=_auth_headers(), params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    # Assuming the API returns a JSON array under the key 'invoices'
    return data.get('invoices', [])

def download_invoice_xml(invoice_id: str) -> str:
    """Download the raw XML content of a single invoice.

    Args:
        invoice_id: Identifier of the invoice as provided by the API.

    Returns:
        The XML content as a string.
    """
    endpoint = f"{SIEG_BASE_URL}/invoices/{invoice_id}/xml"
    response = requests.get(endpoint, headers=_auth_headers(), timeout=30)
    response.raise_for_status()
    # The API returns raw XML; ensure it's decoded as UTF-8 text.
    return response.text
