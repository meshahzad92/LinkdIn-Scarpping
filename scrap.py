from importlib import reload
from Files import constants, functions  # Import modules
from  proxylist import proxy
# Reload modules
reload(constants)
reload(functions)

from Files.constants import *
from Files.functions import *
import time
import re
import random

driver = None


def login(driver, email, password):
    login_Helper(driver, email, password)


def start_browser(proxy=None):
    global driver
    if driver is None:
        driver = start_browser_Helper(proxy)
    return driver


def close_browser():
    global driver
    if driver:
        driver.quit()
        driver = None

def scrape_linkedin_profile(profile_url):
    global driver
    if not driver:
        raise Exception("Browser session not started. Please log in first.")

    open_page(driver, profile_url)

    try:
        # Name
        xpath = "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[2]/div[1]/div[1]/span[1]/a/h1"
        name = get_data(driver, xpath)
        # Number of followers 
        section = get_Followers_section(driver)
        followers_uncleaned = get_Followers(driver, section)
        followers = int(re.sub(r'\D', '', followers_uncleaned[0]))
        # Bio
        xpath = '/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[2]/div[1]/div[2]'
        bio = get_data(driver, xpath)
        # Location
        xpath = '/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[2]/div[2]/span[1]'
        location = get_data(driver, xpath)
        # Education
        section = get_education_section(driver)
        education_data = get_education(driver, section)
        # Contact Info
        path = '/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[2]/div[2]/span[2]/a'
        button_click(driver, path)
        section_xpath = "/html/body/div[4]/div/div/div[2]/section/div"
        contact_info = get_contact_info(driver, section_xpath)
        email = next((info['content'] for info in contact_info if '@' in info.get('content', "")), None)
        # Experience
        experience_list = get_experience(driver,profile_url)
        # Skills
        skills_list = get_skills(driver, profile_url)

        # Random delay to mimic human activity
        delay = random.randint(10, 20)
        print(f"Pausing for {delay} seconds...")
        time.sleep(delay)
        return {    
            "name": name,
            "followers": followers,
            "email": email,
            "bio": bio,
            "location": location,
            "experience": list(experience_list) if isinstance(experience_list, set) else experience_list,
            "education": education_data,
            "skills": list(skills_list) if isinstance(skills_list, set) else skills_list,
        }


    except Exception as e:
        driver.quit()
        raise e