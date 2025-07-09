# routes/favicon.py

from flask import Blueprint, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
from config import Config
from utils import resolve_url, create_response

favicon_bp = Blueprint('favicon', __name__)

@favicon_bp.route('/favicon_checker', methods=['GET'])
def favicon_checker():
    """
    Checks for favicons and web app manifests for a given URL.
    """
    target_url = request.args.get('url')

    if not target_url:
        response, status_code = create_response(
            success=False,
            message='URL parameter is missing.',
            errors=['URL parameter is missing.'],
            status_code=400
        )
        return jsonify(response), status_code

    # Basic URL validation
    if not re.match(r"^(?:f|ht)tps?://", target_url):
        target_url = "http://" + target_url

    response_data = {
        'url': target_url,
        'favicon': None,
        'manifest': None,
        'hasFavicon': False,
        'hasManifest': False,
        'errors': []
    }

    try:
        # Fetch HTML content
        try:
            # Set a realistic User-Agent header
            req_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
            }
            html_response = requests.get(target_url, headers=req_headers, allow_redirects=True, timeout=10)
            html_response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            html_content = html_response.text

        except requests.exceptions.RequestException as e:
            error_message = f'Could not fetch content from the URL: {e}'
            response_data['errors'].append(error_message)
            response, status_code = create_response(
                success=False,
                message='Could not fetch content from the URL. It might be down or blocking requests.',
                data=response_data,
                errors=response_data['errors'],
                status_code=500
            )
            return jsonify(response), status_code

        # Parse HTML
        soup = BeautifulSoup(html_content, 'lxml') # Using lxml for better performance and robustness

        # --- Check for Favicon ---
        favicon_links = soup.find_all('link', rel=['icon', 'shortcut icon', 'apple-touch-icon', 'mask-icon'])
        if favicon_links:
            for link in favicon_links:
                href = link.get('href')
                if href:
                    favicon_full_url = resolve_url(target_url, href)
                    response_data['favicon'] = favicon_full_url
                    response_data['hasFavicon'] = True
                    break # Take the first one found
        else:
            response_data['errors'].append('No standard favicon link found in HTML.')

        # --- Unified Web App Manifest Check ---
        manifest_found = False
        manifest_url = None

        # 1. Try to find manifest linked in HTML
        manifest_link = soup.find('link', rel='manifest')
        if manifest_link:
            linked_manifest_href = manifest_link.get('href')
            if linked_manifest_href:
                manifest_url = resolve_url(target_url, linked_manifest_href)
                manifest_found = True

        # 2. If not found in HTML, check for site.webmanifest at root
        if not manifest_found:
            parsed_url = urlparse(target_url)
            root_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
            site_webmanifest_url = f"{root_domain}/site.webmanifest"

            try:
                # Use HEAD request to check for existence without downloading content
                manifest_head_response = requests.head(site_webmanifest_url, headers=req_headers, timeout=5)
                if manifest_head_response.status_code >= 200 and manifest_head_response.status_code < 300:
                    manifest_url = site_webmanifest_url
                    manifest_found = True
            except requests.exceptions.RequestException:
                # Ignore errors for HEAD request, just means it's not there or accessible
                pass

        response_data['hasManifest'] = manifest_found
        response_data['manifest'] = manifest_url

        if not manifest_found:
            response_data['errors'].append('Web App Manifest not found (neither linked in HTML nor at /site.webmanifest).')

        response, status_code = create_response(
            success=True,
            message='Favicon and Web App Manifest checks completed.',
            data=response_data,
            status_code=200
        )
        return jsonify(response), status_code

    except Exception as e:
        response_data['errors'].append(f'An unexpected error occurred: {e}')
        response, status_code = create_response(
            success=False,
            message=f'An unexpected error occurred: {e}',
            data=response_data,
            errors=response_data['errors'],
            status_code=500
        )
        return jsonify(response), status_code