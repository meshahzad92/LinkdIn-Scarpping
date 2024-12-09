import json
from flask import Flask, request, jsonify
from scrap import start_browser, close_browser, login, scrape_linkedin_profile

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, the server is up and running!"

@app.route('/login', methods=['POST'])
def login_endpoint():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({"error": "Email and password are required."}), 400

    try:
        driver = start_browser()
        login(driver, email, password)
        return jsonify({"message": "Logged in successfully!"}), 200
    except Exception as e:
        close_browser()
        return jsonify({"error": str(e)}), 500

@app.route('/scrape', methods=['POST'])
def scrape_endpoint():
    data = request.get_json()
    profile_urls = data.get('profile_urls')

    if not profile_urls or not isinstance(profile_urls, list):
        return jsonify({"error": "A list of profile URLs is required"}), 400

    scraped_profiles = []
    errors = []

    for i, profile_url in enumerate(profile_urls):
        try:
            scraped_data = scrape_linkedin_profile(profile_url)
            scraped_profiles.append(scraped_data)
        except Exception as e:
            errors.append({"profile_url": profile_url, "error": str(e)})

        # Rate limit to avoid detection
        if i % 10 == 0:
            print("Pausing for 30 seconds to avoid rate limits...")
            import time
            time.sleep(30)  # Pause every 10 profiles

    return jsonify({
        "scraped_profiles": scraped_profiles,
        "errors": errors
    }), 200

@app.route('/logout', methods=['POST'])
def logout_endpoint():
    try:
        close_browser()
        return jsonify({"message": "Logged out and session closed!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
