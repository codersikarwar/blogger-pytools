# app.py (or package_manager_final.py)

from flask import Flask, request, render_template_string, redirect, url_for
import subprocess
import sys
import os

app = Flask(__name__)

# --- HTML Template ---
# This template displays installed packages with delete buttons and a form to install new ones.
# It uses basic inline CSS for styling to keep it self-contained for QPython3L.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Package Manager</title>
    <link href="https://unpkg.com/tailwindcss@^2/dist/tailwind.min.css" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f0f2f5;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            padding: 20px;
            box-sizing: border-box;
            color: #333;
        }
        .container {
            background-color: #ffffff;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            max-width: 900px;
            width: 100%;
            margin-top: 20px;
        }
        h1 {
            color: #4a90e2;
            margin-bottom: 20px;
            font-size: 2.5em;
            text-align: center;
        }
        h2 {
            color: #333;
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 1.8em;
            border-bottom: 1px solid #eee;
            padding-bottom: 5px;
        }
        .package-list {
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            background-color: #f9f9f9;
        }
        .package-item {
            padding: 8px 0;
            border-bottom: 1px dashed #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
        }
        .package-item:last-child {
            border-bottom: none;
        }
        .package-info {
            flex-grow: 1;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .package-name {
            font-weight: bold;
            color: #555;
        }
        .package-version {
            font-size: 0.9em;
            color: #777;
            margin-left: 10px;
        }
        .install-form, .delete-form {
            display: flex;
            flex-direction: column;
            gap: 15px;
            margin-top: 20px;
        }
        .delete-form {
            margin-top: 0;
            flex-direction: row;
            align-items: center;
            justify-content: flex-end;
            width: auto;
        }
        input[type="text"] {
            padding: 12px 15px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 1em;
            width: 100%;
            box-sizing: border-box;
        }
        button {
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-size: 1.1em;
            cursor: pointer;
            transition: background-color 0.3s ease, transform 0.2s ease;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
            white-space: nowrap;
        }
        .install-button {
            background-color: #28a745;
            color: white;
        }
        .install-button:hover {
            background-color: #218838;
            transform: translateY(-2px);
        }
        .delete-button {
            background-color: #dc3545;
            color: white;
            font-size: 0.9em;
            padding: 8px 12px;
        }
        .delete-button:hover {
            background-color: #c82333;
            transform: translateY(-2px);
        }
        .message-box {
            margin-top: 20px;
            padding: 15px;
            border-radius: 8px;
            font-size: 1em;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .message-success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .message-error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .message-info {
            background-color: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        /* Responsive adjustments */
        @media (max-width: 600px) {
            h1 {
                font-size: 2em;
            }
            h2 {
                font-size: 1.5em;
            }
            button {
                font-size: 1em;
                padding: 10px 15px;
            }
            .container {
                padding: 15px;
            }
            .package-list {
                max-height: 200px;
            }
            .package-item {
                flex-direction: column;
                align-items: flex-start;
                gap: 5px;
            }
            .package-info {
                width: 100%;
            }
            .delete-form {
                width: 100%;
                justify-content: flex-start;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Package Manager</h1>

        {% if message %}
            <div class="message-box {{ message_class }}">
                {{ message }}
            </div>
        {% endif %}

        <h2>Installed Packages</h2>
        <div class="package-list">
            {% if packages %}
                {% for package in packages %}
                    <div class="package-item">
                        <div class="package-info">
                            <span class="package-name">{{ package.name }}</span>
                            <span class="package-version">{{ package.version }}</span>
                        </div>
                        <form action="{{ url_for('uninstall_package') }}" method="POST" class="delete-form">
                            <input type="hidden" name="package_name" value="{{ package.name }}">
                            <button type="submit" class="delete-button">Delete</button>
                        </form>
                    </div>
                {% endfor %}
            {% else %}
                <p>No packages found or unable to list packages.</p>
            {% endif %}
        </div>

        <h2>Install New Package</h2>
        <form action="{{ url_for('install_package') }}" method="POST" class="install-form">
            <input type="text" name="package_name" placeholder="Enter package name (e.g., requests, beautifulsoup4)" required>
            <button type="submit" class="install-button">Install Package</button>
        </form>
    </div>
</body>
</html>
"""

# --- Helper Functions ---

def get_installed_packages():
    """
    Executes 'pip list' and parses the output to get installed packages.
    Returns a list of dictionaries with 'name' and 'version'.
    """
    try:
        # Use sys.executable to ensure the correct pip is called
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list"],
            capture_output=True, text=True, check=True
        )
        lines = result.stdout.strip().split('\n')
        packages = []
        # Skip header lines (e.g., "Package    Version", "---------- -------")
        if len(lines) > 2:
            for line in lines[2:]:
                parts = line.strip().split()
                if len(parts) >= 2:
                    name = parts[0]
                    version = parts[-1]
                    packages.append({"name": name, "version": version})
        return packages
    except subprocess.CalledProcessError as e:
        print(f"Error listing packages: {e.stderr}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while listing packages: {e}")
        return []

def install_python_package(package_name):
    """
    Executes 'pip install' for the given package name.
    Returns a tuple (success: bool, output: str).
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package_name],
            capture_output=True, text=True, check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr
    except Exception as e:
        return False, f"An unexpected error occurred: {e}"

def uninstall_python_package(package_name):
    """
    Executes 'pip uninstall -y' for the given package name.
    Returns a tuple (success: bool, output: str).
    """
    try:
        # The -y flag automatically confirms the uninstallation
        result = subprocess.run(
            [sys.executable, "-m", "pip", "uninstall", "-y", package_name],
            capture_output=True, text=True, check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr
    except Exception as e:
        return False, f"An unexpected error occurred: {e}"

# --- Flask Routes ---

@app.route('/', methods=['GET'])
def home():
    """
    Displays the list of installed packages and the installation form.
    Handles messages from previous installations/uninstallations.
    """
    packages = get_installed_packages()
    message = request.args.get('message')
    message_class = request.args.get('message_class', 'message-info')
    return render_template_string(HTML_TEMPLATE, packages=packages, message=message, message_class=message_class)

@app.route('/install', methods=['POST'])
def install_package():
    """
    Handles the package installation request from the form.
    Redirects back to the home page with a status message.
    """
    package_name = request.form.get('package_name')
    if not package_name:
        return redirect(url_for('home', message="Package name cannot be empty.", message_class="message-error"))

    success, output = install_python_package(package_name)

    if success:
        msg = f"Successfully installed '{package_name}'.\n\nOutput:\n{output}"
        msg_class = "message-success"
    else:
        msg = f"Failed to install '{package_name}'.\n\nError:\n{output}"
        msg_class = "message-error"

    return redirect(url_for('home', message=msg, message_class=msg_class))

@app.route('/uninstall', methods=['POST'])
def uninstall_package():
    """
    Handles the package uninstallation request from the form.
    Redirects back to the home page with a status message.
    """
    package_name = request.form.get('package_name')
    if not package_name:
        return redirect(url_for('home', message="Package name cannot be empty for uninstallation.", message_class="message-error"))

    success, output = uninstall_python_package(package_name)

    if success:
        msg = f"Successfully uninstalled '{package_name}'.\n\nOutput:\n{output}"
        msg_class = "message-success"
    else:
        msg = f"Failed to uninstall '{package_name}'.\n\nError:\n{output}"
        msg_class = "message-error"

    return redirect(url_for('home', message=msg, message_class=msg_class))


# --- Run the Flask App ---
if __name__ == '__main__':
    print("Starting Flask Package Manager...")
    print("Access it at: http://localhost:5000")
    print("Or use your device's IP address (e.g., http://192.168.1.x:5000)")
    # IMPORTANT: debug=False and use_reloader=False are crucial for QPython3L
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

