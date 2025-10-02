# routes/minify_html.py

from flask import Blueprint, request, jsonify
# re and json are no longer strictly needed but kept if other utility functions need them
import re 
import json
# Import the htmlmin library
from htmlmin.main import minify as html_minify

# Assuming 'create_response' is imported from 'utils' as in your favicon.py example
from utils import create_response

minify_html_bp = Blueprint('minify_html', __name__)

@minify_html_bp.route('/minify_html', methods=['POST'])
def minify_html_checker():
    """
    Minifies HTML content based on POST data and options using the htmlmin library.
    Consistent with the structure of favicon.py.
    """
    
    # 1. Get data from JSON body (preferred) or form data (for traditional POSTs)
    try:
        data = request.get_json() or request.form
    except Exception:
        # Fallback if the body is not valid JSON
        data = request.form if request.form else {}
        
    html_content = data.get('html_code', '')
    
    # Checkbox values from client usually come as 'true'/'false' strings
    remove_comments_str = data.get('remove_comments', 'false').lower()
    remove_comments = remove_comments_str == 'true'

    # Basic validation: ensure HTML content is not empty
    if not html_content:
        response, status_code = create_response(
            success=False,
            message='No HTML code provided for minification.',
            errors=['html_code parameter is missing or empty.'],
            status_code=400
        )
        return jsonify(response), status_code

    # --- HTML Minification Logic (Using htmlmin) ---
    try:
        minified_html = html_minify(
            html_content,
            remove_comments=remove_comments,
            # These options provide optimal minification:
            remove_empty_space=True, 
            reduce_empty_attributes=True,
            remove_optional_attribute_quotes=False # Safer for wide compatibility
        )

        response_data = {
            'minified_html': minified_html,
            'original_length': len(html_content),
            'minified_length': len(minified_html),
            'removed_comments': remove_comments
        }
        
        # Return the final result using your utility function
        response, status_code = create_response(
            success=True,
            message='HTML content successfully minified.',
            data=response_data,
            status_code=200
        )
        return jsonify(response), status_code

    except Exception as e:
        error_message = f'An unexpected error occurred during minification: {e}'
        response_data = {
            'minified_html': html_content, # Return original content on failure
            'original_length': len(html_content),
            'minified_length': len(html_content),
            'removed_comments': remove_comments
        }
        
        response, status_code = create_response(
            success=False,
            message=error_message,
            data=response_data,
            errors=[error_message],
            status_code=500
        )
        return jsonify(response), status_code
