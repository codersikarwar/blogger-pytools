<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+"/>
  <img src="https://img.shields.io/badge/Flask-2.0+-black?style=for-the-badge&logo=flask&logoColor=white" alt="Flask 2.0+"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License: MIT"/>
</p>
<h1 align="center">Site Tools API</h1>

---

## Description

This is a lightweight **Flask microservice API** providing essential web development and SEO utility endpoints. It includes tools for **favicon/manifest checks**, **HTML minification**, **HTTP header inspection**, **privacy policy generation**, and **WHOIS domain lookups**.

The API is built to help developers and website owners quickly retrieve, process, and generate common web assets and data. It leverages powerful Python libraries like `requests`, `BeautifulSoup`, and `python-whois` to deliver robust results in a structured JSON format.

---

## Installation

### Prerequisites

You need **Python 3.8+** and **`pip`** installed.

### Setup

1.  **Clone the Repository:**
    ```
    git clone [YOUR_REPO_URL]
    cd [YOUR_REPO_DIRECTORY]
    ```

2.  **Install Dependencies:**
    Ensure all required libraries are installed using the `requirements.txt` file:

    ```
    pip install -r requirements.txt
    ```

3.  **Run the Application:**
    Assuming your main application file is `app.py`:

    ```
    export FLASK_APP=app.py
    flask run
    ```
    The API will typically start running at `http://127.0.0.1:5000/`.

---

## Usage (API Endpoints)

All endpoints return results in a consistent JSON format.

### 1. Favicon and Manifest Checker

Checks for favicon links, Apple Touch Icons, and Web App Manifests.

* **Endpoint:** `/favicon_checker`
* **Method:** `GET`
* **Parameter:** `url` (string, required)

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `url` | Query | The target website URL (e.g., `https://google.com`). |

**Example Request:**
```
GET /favicon_checker?url=https://www.google.com
```

---

### 2. HTML Minifier

Minifies raw HTML content using the robust `htmlmin` library.

* **Endpoint:** `/minify_html`
* **Method:** `POST`
* **Parameters:** Sent in the **JSON body** or **Form Data**.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `html_code` | String | The raw HTML to be minified. |
| `remove_comments` | Boolean (String) | Set to `"true"` to strip HTML comments. |

**Example Request (JSON Body):**
```
{
    "html_code": "<html>\n  <body>\n    \n  </body>\n</html>",
    "remove_comments": "true" 
}
```

---

### 3. HTTP Header Checker

Retrieves all response headers, status code, and final URL after redirects.

* **Endpoint:** `/header_checker`
* **Method:** `GET`
* **Parameter:** `url` (string, required)

| Parameter | Type  | Description                          |
| :-------- | :---- | :----------------------------------- |
| `url`     | Query | The target URL to check headers for. |

**Example Request:**
```
GET /header_checker?url=https://www.github.com
```

---

### 4. Privacy Policy Generator

Generates a basic HTML-formatted Privacy Policy.

* **Endpoint:** `/privacy_policy`
* **Method:** `POST`
* **Parameters:** Sent in the **JSON body** or **Form Data**.

| Parameter         | Type             | Description                                                      |
| :---------------- | :--------------- | :--------------------------------------------------------------- |
| `website_name`    | String           | Your website's name.                                             |
| `website_url`     | String           | Your website's URL.                                              |
| `contact_email`   | String           | Your contact email for policy questions.                         |
| `uses_ga`         | Boolean (String) | Set to "true" if you use Google Analytics.                       |
| `uses_adsense`    | Boolean (String) | Set to "true" if you use Google AdSense.                         |
| `collects_emails` | Boolean (String) | Set to "true" if you actively collect emails (e.g., newsletter). |

**Example Request (JSON Body):**

```
{
    "website_name": "Example Site",
    "website_url": "https://www.examplesite.com",
    "contact_email": "contact@examplesite.com",
    "uses_ga": "true",
    "uses_adsense": "false",
    "collects_emails": "true"
}
```

---

### 5. WHOIS Domain Checker

Performs a WHOIS lookup to retrieve registration status and details for a domain.

* **Endpoint:** `/whois_checker`
* **Method:** `GET`
* **Parameter:** `domain` (string, required)

| Parameter | Type  | Description                                  |
| :-------- | :---- | :------------------------------------------- |
| `domain`  | Query | The domain name to check (e.g., google.com). |

**Example Request:**
```
GET /whois_checker?domain=google.com
```

---
