# routes/header_checker.py

from flask import Blueprint, request, jsonify
import requests
from urllib.parse import urlparse, urlunparse
import re

# Assuming 'create_response' is imported from 'utils'
from utils import create_response

header_checker_bp = Blueprint('header_checker', __name__)

# Dictionary of common status messages (as found in your PHP)
STATUS_MESSAGES = {
    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    204: 'No Content',
    301: 'Moved Permanently',
    302: 'Found',
    303: 'See Other',
    304: 'Not Modified',
    307: 'Temporary Redirect',
    308: 'Permanent Redirect',
    400: 'Bad Request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    429: 'Too Many Requests',
    500: 'Internal Server Error',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Timeout'
}

def get_status_message(status_code):
    """
    Retrieves a human-readable status message for an HTTP status code.
    """
    return STATUS_MESSAGES.get(status_code, 'Unknown Status')

@header_checker_bp.route('/header_checker', methods=['GET'])
def header_checker():
    """
    Fetches HTTP headers for a given URL using a HEAD request.
    """
    target_url = request.args.get('url')

    # 1. URL Parameter Check (PHP: if (empty($url)))
    if not target_url:
        response, status_code = create_response(
            success=False,
            message='URL parameter is missing.',
            errors=['No URL provided in the request.'],
            status_code=400
        )
        return jsonify(response), status_code

    # 2. Basic URL Validation (PHP: filter_var($url, FILTER_VALIDATE_URL))
    # We'll use a regex check similar to favicon.py to allow non-schemed URLs
    if not re.match(r"^(?:f|ht)tps?://", target_url):
        target_url = "http://" + target_url
    
    # We'll perform a simple check to ensure it looks like a URL before attempting the request
    try:
        parsed = urlparse(target_url)
        if not all([parsed.scheme, parsed.netloc]):
            raise ValueError("Invalid structure")
    except ValueError:
        response, status_code = create_response(
            success=False,
            message='Invalid URL format.',
            errors=['The provided URL does not appear to be a valid URL.'],
            status_code=400
        )
        return jsonify(response), status_code

    response_data = {
        'url': target_url,
        'status_code': None,
        'status_message': 'Request Failed',
        'headers': {},
        'errors': []
    }
    
    # Set headers similar to favicon.py for consistency
    req_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }

    try:
        # Use requests.head() to mimic PHP's CURLOPT_NOBODY, but follow redirects
        # requests automatically handles redirects (CURLOPT_FOLLOWLOCATION)
        # requests verifies SSL by default (CURLOPT_SSL_VERIFYPEER/HOST)
        http_response = requests.head(
            target_url, 
            headers=req_headers, 
            allow_redirects=True, 
            timeout=10 # CURLOPT_TIMEOUT
        )
        
        # requests.head() is often blocked, so fall back to requests.get() 
        # but stop downloading content immediately (stream=True)
        if http_response.status_code >= 400:
             http_response = requests.get(
                target_url, 
                headers=req_headers, 
                allow_redirects=True, 
                timeout=10,
                stream=True
            )
             # Important: Stop the download immediately
             if http_response.raw:
                 http_response.raw.close()
            

        # Get final status code and message
        final_status_code = http_response.status_code
        final_status_message = get_status_message(final_status_code)
        
        # requests returns headers as a CaseInsensitiveDict
        response_data['headers'] = dict(http_response.headers)
        response_data['status_code'] = final_status_code
        response_data['status_message'] = final_status_message
        
        # If there were redirects, get the final URL
        if http_response.history:
            response_data['url'] = http_response.url
        
        response, status_code = create_response(
            success=True,
            message='Successfully retrieved HTTP headers.',
            data=response_data,
            status_code=200
        )
        return jsonify(response), status_code

    except requests.exceptions.Timeout as e:
        error_message = f'Request timed out after 10 seconds.'
        response_data['errors'].append(error_message)
        response, status_code = create_response(
            success=False,
            message='Failed to fetch URL headers: Timeout.',
            data=response_data,
            errors=response_data['errors'],
            status_code=500
        )
        return jsonify(response), status_code
        
    except requests.exceptions.RequestException as e:
        error_message = f'Failed to connect or resolve URL: {e}'
        response_data['errors'].append(error_message)
        response, status_code = create_response(
            success=False,
            message='Failed to fetch URL headers.',
            data=response_data,
            errors=response_data['errors'],
            status_code=500
        )
        return jsonify(response), status_code

    except Exception as e:
        error_message = f'An unexpected error occurred: {e}'
        response_data['errors'].append(error_message)
        response, status_code = create_response(
            success=False,
            message=error_message,
            data=response_data,
            errors=response_data['errors'],
            status_code=500
        )
        return jsonify(response), status_code
