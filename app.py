# app.py

from flask import Flask, jsonify
from flask_cors import CORS # For handling Cross-Origin Resource Sharing
from config import Config
from routes.favicon import favicon_bp
from routes.dns import dns_bp
from routes.minify_html import minify_html_bp
from routes.header_checker import header_checker_bp
from routes.policy_generator import policy_generator_bp
from routes.whois_checker import whois_checker_bp
from utils import create_response

app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

# Initialize CORS with your allowed origin
# You can also configure CORS per blueprint or route if needed
CORS(app, resources={r"/*": {"origins": Config.CORS_ALLOW_ORIGIN}})

# Register blueprints
app.register_blueprint(favicon_bp)
app.register_blueprint(dns_bp)
app.register_blueprint(minify_html_bp)
app.register_blueprint(header_checker_bp) 
app.register_blueprint(policy_generator_bp) 
app.register_blueprint(whois_checker_bp) 

# --- Global Error Handlers ---
@app.errorhandler(404)
def not_found_error(error):
    response, status_code = create_response(
        success=False,
        message="The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.",
        errors=["Not Found"],
        status_code=404
    )
    return jsonify(response), status_code


@app.errorhandler(500)
def internal_error(error):
    response, status_code = create_response(
        success=False,
        message="An internal server error occurred. Please try again later.",
        errors=["Internal Server Error"],
        status_code=500
    )
    return jsonify(response), status_code

# --- Root Endpoint (Optional, for testing API health) ---
@app.route('/')
def index():
    response, status_code = create_response(
        success=True,
        message="Welcome to the Modular API! Check /favicon_checker or /dns_lookup.",
        data={"api_version": "1.0"}
    )
    return jsonify(response), status_code

if __name__ == '__main__':
    print(f"Starting Flask Endpoints on {Config.CORS_ALLOW_ORIGIN}...")
    print("Favicon Checker: http://localhost:5000/favicon_checker?url=https://www.google.com")
    print("DNS Lookup: http://localhost:5000/dns_lookup?domain=example.com")
    # For development:
    app.run(host='0.0.0.0', port=5000, debug=True)
    # For production, set debug=False and use a WSGI server like Gunicorn or uWSGI
