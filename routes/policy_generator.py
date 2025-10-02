# routes/policy_generator.py

from flask import Blueprint, request, jsonify
import re
from datetime import datetime
from utils import create_response

policy_generator_bp = Blueprint('policy_generator', __name__)

# Basic function to check if a string is a valid email
def is_valid_email(email):
    """Simple regex check for email validity."""
    # This is not perfect but mirrors server-side validation intent
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_regex, email)

# Basic function to check if a string is a valid URL (with http/https assumed)
def is_valid_url(url):
    """Simple check for URL validity, allowing non-schemed URLs."""
    # Check if a scheme exists, if not, try with http://
    if not re.match(r"^(?:f|ht)tps?://", url):
        url = "http://" + url
    
    # Python's re.match is usually sufficient for basic validation
    # This regex is a simplified check for a domain structure.
    url_regex = (
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
        r'localhost|' # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$'
    )
    return re.match(url_regex, url, re.IGNORECASE) is not None

@policy_generator_bp.route('/privacy_policy', methods=['POST'])
def privacy_policy_generator():
    """
    Generates a basic Privacy Policy HTML based on user input from a POST request.
    """
    
    # 1. Get data from JSON body or form data (consistent with minify_html.py)
    try:
        data = request.get_json() or request.form
    except Exception:
        data = request.form if request.form else {}
        
    # Retrieve and clean input data (Flask handles URL/email encoding, so simple .get() is okay)
    website_name = data.get('website_name', '').strip()
    website_url = data.get('website_url', '').strip()
    contact_email = data.get('contact_email', '').strip()
    
    # Convert string 'true'/'false' to boolean
    uses_ga = data.get('uses_ga', 'false').lower() == 'true'
    uses_adsense = data.get('uses_adsense', 'false').lower() == 'true'
    collects_emails = data.get('collects_emails', 'false').lower() == 'true'
    
    # --- Server-Side Validation ---
    errors = []
    if not website_name or not website_url or not contact_email:
        errors.append('All basic fields (Website Name, URL, Contact Email) are required.')
    
    # The PHP logic only validated the final URL, so we stick to that for parity
    if not is_valid_url(website_url):
        errors.append('Invalid Website URL format.')
        
    if not is_valid_email(contact_email):
        errors.append('Invalid Contact Email format.')
        
    if errors:
        response, status_code = create_response(
            success=False,
            message='Input validation failed.',
            errors=errors,
            status_code=400
        )
        return jsonify(response), status_code

    # --- Start building the Privacy Policy HTML string based on inputs ---
    policy_html = ''
    current_date = datetime.now().strftime('%B %d, %Y')

    policy_html += f'<div style="text-align: left;"><strong>Last Updated: {current_date}</strong></div>'
    policy_html += f'<p>This Privacy Policy explains how we collect, use, and protect your information when you visit <strong>{website_name}</strong> (<a href="{website_url}" target="_blank">{website_url}</a>). By using this website, you agree to the terms outlined below.</p>'
    policy_html += '<p><strong>This policy may be updated or changed at any time without prior notice. Please check this page periodically for updates.</strong></p>'

    policy_html += '<h3>1. Information We Collect</h3>'
    policy_html += '<ul>'
    policy_html += '<li><strong>Non-Personal Information:</strong> such as browser type, IP address, pages visited, and time spent on the site. This is collected through cookies and analytics tools.</li>'
    if collects_emails:
        policy_html += '<li><strong>Personal Information:</strong> such as your name and email address when you contact us, subscribe to a newsletter, or register for services.</li>'
    else:
        policy_html += '<li><strong>Personal Information:</strong> such as your name and email address if you voluntarily provide it (e.g., through a contact form).</li>'
    policy_html += '</ul>'

    policy_html += '<h3>2. How We Use Your Information</h3>'
    policy_html += '<ul>'
    policy_html += '<li>To operate, maintain, and improve our website.</li>'
    policy_html += '<li>To personalize user experience.</li>'
    policy_html += '<li>To respond to messages or inquiries.</li>'
    if collects_emails:
        policy_html += '<li>To send emails (only if you opt-in for newsletters or respond to inquiries).</li>'
    policy_html += '<li>To analyze traffic and prevent abuse.</li>'
    policy_html += '</ul>'

    policy_html += '<h3>3. Log Files</h3>'
    policy_html += f'<p>{website_name} uses standard log files. These include information such as:</p>'
    policy_html += '<ul>'
    policy_html += '<li>IP address</li>'
    policy_html += '<li>Browser type</li>'
    policy_html += '<li>Internet Service Provider (ISP)</li>'
    policy_html += '<li>Date and time stamp</li>'
    policy_html += '<li>Referring/exit pages</li>'
    policy_html += '<li>Number of clicks</li>'
    policy_html += '</ul>'
    policy_html += '<p>This data is used for analytics and server management and is not linked to any personally identifiable information.</p>'

    # Conditional sections based on user checkboxes
    if uses_adsense:
        policy_html += '<h3>4. Google AdSense and Cookies</h3>'
        policy_html += '<p>We use Google AdSense to serve ads.</p>'
        policy_html += '<ul>'
        policy_html += '<li>Google uses cookies to serve personalized ads based on your visits to this and other websites.</li>'
        policy_html += '<li>You can opt out of personalized advertising by visiting <a href="https://www.google.com/settings/ads" target="_blank">Google Ads Settings</a>.</li>'
        policy_html += '<li>More info: <a href="https://policies.google.com/technologies/ads" target="_blank">How Google uses data</a>.</li>'
        policy_html += '</ul>'

    policy_html += '<h3>5. Cookies and Tracking</h3>'
    policy_html += '<p>We use cookies to:</p>'
    policy_html += '<ul>'
    policy_html += '<li>Improve site performance.</li>'
    policy_html += '<li>Understand user behavior.</li>'
    policy_html += f"<li>Serve relevant content and ads{' (if applicable)' if uses_adsense else ''}.</li>"
    policy_html += '</ul>'
    policy_html += '<p>You can disable cookies in your browser settings, but some parts of the site may not function properly.</p>'

    policy_html += '<h3>6. Third-Party Privacy Policies</h3>'
    policy_html += '<p>This policy does not apply to other websites or advertisers that we link to. We recommend reviewing the privacy policies of those sites separately.</p>'
    if uses_ga:
        policy_html += '<h4>Google Analytics</h4>'
        policy_html += '<p>We use Google Analytics to understand how visitors engage with our site. Google Analytics collects information anonymously. It reports website trends without identifying individual visitors. You can opt-out of Google Analytics without affecting how you visit our site – for more information on opting out of being tracked by Google Analytics across all websites you use, visit this Google page: <a href="https://tools.google.com/dlpage/gaoptout" target="_blank">https://tools.google.com/dlpage/gaoptout</a>.</p>'

    policy_html += '<h3>7. Children’s Information</h3>'
    policy_html += f'<p>We do not knowingly collect personal information from children under the age of 13. If you believe your child has provided such information, please contact us at {contact_email} and we will promptly delete it.</p>'

    policy_html += '<h3>8. Changes to This Privacy Policy</h3>'
    policy_html += '<p>We may update our Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page. You are advised to review this Privacy Policy periodically for any changes. Changes to this Privacy Policy are effective when they are posted on this page.</p>'

    policy_html += '<h3>9. Contact Us</h3>'
    policy_html += '<p>If you have any questions about this Privacy Policy, you can contact us:</p>'
    policy_html += '<ul>'
    policy_html += f'<li>By email: <a href="mailto:{contact_email}">{contact_email}</a></li>'
    policy_html += '</ul>'

    response_data = {
        'policy_html': policy_html,
        'website_name': website_name,
        'contact_email': contact_email
    }
    
    # Return the generated HTML policy in a JSON response
    response, status_code = create_response(
        success=True,
        message='Privacy Policy successfully generated.',
        data=response_data,
        status_code=200
    )
    return jsonify(response), status_code
