from flask import Blueprint, request, jsonify
import re
import json
from htmlminifier import minify as html_minify
from utils import create_response

minify_html_bp = Blueprint('minify_html', __name__)

@minify_html_bp.route('/minify_html', methods=['POST'])
def minify_html_checker():
    """
    Minifies HTML content based on POST data and options using the htmlminifier library.
    Consistent with the structure of favicon.py.
    """

    try:
        data = request.get_json() or request.form
    except Exception:
        data = request.form if request.form else {}

    html_content = data.get('html_code', '')

    remove_comments_str = data.get('remove_comments', 'false').lower()
    remove_comments = remove_comments_str == 'true'

    if not html_content:
        response, status_code = create_response(
            success=False,
            message='No HTML code provided for minification.',
            errors=['html_code parameter is missing or empty.'],
            status_code=400
        )
        return jsonify(response), status_code

    try:
        minified_html = html_minify(
            html_content,
            remove_comments=remove_comments,
            remove_empty_space=True,
            reduce_empty_attributes=True,
            remove_optional_attribute_quotes=False
        )

        response_data = {
            'minified_html': minified_html,
            'original_length': len(html_content),
            'minified_length': len(minified_html),
            'removed_comments': remove_comments
        }

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
            'minified_html': html_content,
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

