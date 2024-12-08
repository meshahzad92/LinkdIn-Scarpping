import json
from flask import Flask, request, jsonify
from scrap import scrape_linkedin_profile

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, the server is up and running!"

@app.route('/scrape', methods=['POST'])
def scrape_endpoint():
    # Check if the request contains JSON data
    if request.is_json:
        data = request.get_json()
    else:
        return jsonify({"error": "Request must contain JSON data."}), 400

    # Extract values from the JSON data sent in the request body
    profile_url = data.get('profile_url')
    email = data.get('email')
    password = data.get('password')

    # Print the extracted values (for debugging purposes)
    print(f"Received Data: {data}")
    
    # Check if all necessary fields are provided
    if not all([profile_url, email, password]):
        return jsonify({"error": "profile_url, email, password, and login_page are required"}), 400

    try:
        # Attempt to scrape the LinkedIn profile with the provided data
        scraped_data = scrape_linkedin_profile(profile_url, email, password)
        return jsonify(scraped_data), 200
    except Exception as e:
        # If an error occurs during scraping, return an error message
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
