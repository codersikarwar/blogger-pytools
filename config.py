# config.py

class Config:
    # IMPORTANT: Adjust this for your production environment
    # For local testing, you might use "*" or "http://localhost:5000"
    # For your Blogger site, it should be your Blogger domain.
    CORS_ALLOW_ORIGIN = "https://www.codersikarwar.site" # Or "*" for broader access during development
    # Add other configurations here (e.g., database URIs, API keys)