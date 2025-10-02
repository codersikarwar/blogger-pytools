# routes/whois_checker.py

from flask import Blueprint, request, jsonify
import re
import whois # The python-whois library
from whois.parser import PywhoisError

# Assuming 'create_response' is imported from 'utils'
from utils import create_response

whois_checker_bp = Blueprint('whois_checker', __name__)

@whois_checker_bp.route('/whois_checker', methods=['GET'])
def whois_checker():
    """
    Performs a WHOIS lookup for a given domain name using the python-whois library.
    """
    domain_name = request.args.get('domain')

    response_data = {
        'domain': domain_name,
        'whois_raw': None,
        'is_registered': False,
        'parsed_data': {}
    }

    # 1. Input Check
    if not domain_name:
        response, status_code = create_response(
            success=False,
            message='Please provide a domain name.',
            data=response_data,
            errors=['Domain parameter is missing.'],
            status_code=400
        )
        return jsonify(response), status_code

    # 2. Basic Domain Validation (Simplified regex to match PHP's intent)
    # The library handles most TLD rules, but we'll keep the basic check.
    if not re.match(r'^([a-z0-9-]+\.)+[a-z]{2,63}$', domain_name, re.IGNORECASE):
        response, status_code = create_response(
            success=False,
            message='Invalid domain format. Please enter a valid domain (e.g., example.com).',
            data=response_data,
            errors=['Invalid domain format.'],
            status_code=400
        )
        return jsonify(response), status_code

    try:
        # The whois library handles server mapping, connection, and parsing automatically.
        # It raises PywhoisError for "not found" or connection issues.
        w = whois.query(domain_name, timeout=10)
        
        # Check if the domain is registered. 
        # The query() method returns None if the domain is not found.
        if w is None:
            response_data['is_registered'] = False
            message = f"No WHOIS information found for '{domain_name}'. It is likely unregistered."
        else:
            # Domain found, pull raw data and parsed data
            response_data['is_registered'] = True
            response_data['whois_raw'] = w.text
            
            # Convert the whois object properties (like expiration_date, registrar) to a dictionary
            # The library does smart parsing, which is more useful than just raw text
            response_data['parsed_data'] = {
                'registrar': w.registrar,
                'creation_date': str(w.creation_date),
                'expiration_date': str(w.expiration_date),
                'last_updated': str(w.last_updated),
                'name_servers': w.name_servers,
                'emails': w.emails
            }
            message = 'WHOIS lookup successful.'
            
        response_data['domain'] = domain_name

        response, status_code = create_response(
            success=True if w else False,
            message=message,
            data=response_data,
            status_code=200
        )
        return jsonify(response), status_code

    except PywhoisError as e:
        # This typically catches connection errors, lookup errors, or specific "not found" messages.
        # The library often returns the raw text even on failure, but we prioritize the error message.
        error_message = f"WHOIS lookup failed: {str(e)}"
        
        # A common failure message from the library means 'not found'
        is_not_registered = "no matching record" in str(e).lower() or "no data found" in str(e).lower()

        if is_not_registered:
            message = f"No WHOIS information found for '{domain_name}'. It is likely unregistered or the WHOIS server returned an error."
            success = False
        else:
            message = f"WHOIS query failed due to a server or connection error: {str(e)}"
            success = False

        response_data['errors'] = [message]
        
        response, status_code = create_response(
            success=success,
            message=message,
            data=response_data,
            errors=response_data['errors'],
            status_code=500
        )
        return jsonify(response), status_code

    except Exception as e:
        error_message = f'An unexpected error occurred: {e}'
        response_data['errors'] = [error_message]
        
        response, status_code = create_response(
            success=False,
            message=error_message,
            data=response_data,
            errors=response_data['errors'],
            status_code=500
        )
        return jsonify(response), status_code
