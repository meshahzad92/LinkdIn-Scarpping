import json
from flask import Flask, request, jsonify
from scrap import start_browser, close_browser, login, scrape_linkedin_profile
import random
from proxylist import proxy
from Files.functions import start_browser_Helper
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
        index = random.randint(0, len(proxy) - 1)
        print('\n\nUsing proxy:', proxy[index])
        print('\n\n')
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

    if not all([profile_urls]):
        return jsonify({"error": "profile_urls required"}), 400

    scraped_profiles = []
    errors = []

    for i, profile_url in enumerate(profile_urls):
        try:
            scraped_data = scrape_linkedin_profile(profile_url)
            scraped_profiles.append(scraped_data)
        except Exception as e:
            errors.append({"profile_url": profile_url, "error": str(e)})

        if i % 10 == 0:
            print("Pausing for 30 seconds to avoid rate limits...")
            import time
            time.sleep(5)  

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
