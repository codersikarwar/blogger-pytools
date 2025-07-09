# utils.py

from urllib.parse import urljoin
import dns.rdatatype

def resolve_url(base_url, relative_url):
    """
    Resolves a relative URL against a base URL.
    Equivalent to PHP's resolve_url function using urllib.parse.urljoin.
    """
    return urljoin(base_url, relative_url)

def get_record_type_name(rdtype):
    """
    Helper function to get readable DNS record type names from dnspython rdtype objects.
    """
    return dns.rdatatype.to_text(rdtype)

def create_response(success, message, data=None, errors=None, status_code=200):
    """
    Creates a standardized JSON response dictionary.
    """
    if data is None:
        data = {}
    if errors is None:
        errors = []

    response = {
        'success': success,
        'message': message,
        'data': data,
        'errors': errors
    }
    return response, status_code