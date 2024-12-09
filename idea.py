from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import random
import redis
import requests
from typing import List, Dict
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

app = FastAPI()

# Setup Redis client for session management
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# Proxy pool (use rotating proxies or third-party service)
PROXY_POOL = ["proxy1", "proxy2", "proxy3"]  # You can use a service like ProxyMesh

# Simulated user login data (use environment variables or secure method in production)
USER_CREDENTIALS = {
    'email': 'your_email@example.com',
    'password': 'your_password'
}

# Function to initialize Selenium WebDriver with proxy
def init_driver(proxy=None):
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode to save resources
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # Use proxy if provided
    if proxy:
        chrome_options.add_argument(f'--proxy-server={proxy}')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

# Function to login and maintain the session
def login_to_linkedin(driver):
    driver.get("https://www.linkedin.com/login")
    driver.find_element(By.ID, "username").send_keys(USER_CREDENTIALS['email'])
    driver.find_element(By.ID, "password").send_keys(USER_CREDENTIALS['password'])
    driver.find_element(By.XPATH, "//button[text()='Sign in']").click()
    time.sleep(3)  # Wait for the login to complete

# Function to scrape LinkedIn profile data
def scrape_profile_data(driver, profile_url):
    driver.get(profile_url)
    time.sleep(2)
    
    try:
        name = driver.find_element(By.XPATH, "//h1").text
        bio = driver.find_element(By.XPATH, "//section[@class='pv-about-section']//span").text
        location = driver.find_element(By.XPATH, "//span[@class='text-body-small']").text
        followers = driver.find_element(By.XPATH, "//span[text()='Followers']").text
        return {"name": name, "bio": bio, "location": location, "followers": followers}
    except Exception as e:
        return {"error": str(e)}

# Model to represent login request data
class LoginRequest(BaseModel):
    user_id: str

# Model to represent scraping request data
class ScrapeRequest(BaseModel):
    user_id: str
    profile_url: str

# Login endpoint
@app.post("/login")
async def login(request: LoginRequest):
    user_id = request.user_id
    if redis_client.exists(user_id):
        raise HTTPException(status_code=400, detail="User already logged in")

    # Start Selenium browser with a proxy from pool
    proxy = random.choice(PROXY_POOL)
    driver = init_driver(proxy)
    login_to_linkedin(driver)

    # Store the Selenium driver instance in Redis
    redis_client.set(user_id, driver.session_id)
    return {"message": "Logged in successfully"}

# Scrape profile data endpoint
@app.post("/scrape")
async def scrape(request: ScrapeRequest):
    user_id = request.user_id
    profile_url = request.profile_url

    # Check if the user has an active session
    if not redis_client.exists(user_id):
        raise HTTPException(status_code=400, detail="User not logged in")

    # Retrieve the driver session ID from Redis
    session_id = redis_client.get(user_id)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))  # Retrieve driver session if possible

    # Scrape the profile data
    data = scrape_profile_data(driver, profile_url)
    return {"data": data}

# Logout endpoint
@app.post("/logout")
async def logout(request: LoginRequest):
    user_id = request.user_id
    if not redis_client.exists(user_id):
        raise HTTPException(status_code=400, detail="User not logged in")

    # Retrieve the driver session and quit the browser
    session_id = redis_client.get(user_id)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))  # Retrieve driver session
    driver.quit()

    # Delete the session from Redis
    redis_client.delete(user_id)
    return {"message": "Logged out successfully"}

