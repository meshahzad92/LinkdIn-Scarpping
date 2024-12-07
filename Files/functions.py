from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from scipy.interpolate import interp1d
import re
import csv

def start_browser():
    '''
    Initializes the WebDriver in headless mode and returns the driver instance.
    '''
    options = Options()
    # options.add_argument("--headless")  
    driver = webdriver.Edge(options=options)
    return driver

def open_page(driver ,link):
    '''
    Load the given URL and wait until the page is fully loaded.
    If the page does not load within 10 seconds, an exception will be raised.
    '''
    driver.get(link)
    wait_for_page_load(driver)
    assert "No results found." not in driver.page_source

def wait_for_page_load(driver, timeout=4):
    '''
    Wait for the page to load within the given timeout period.
    If the page does not load in the specified time, an exception is raised.
    '''
    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    except Exception as e:
        print(f"Error while waiting for page load: {e}")

def button_click(driver, xpath):
    '''
    Wait for a button to be clickable and then click it.
    '''
    try:
        # Wait for the button to be clickable
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))

        # Find the button element by XPath
        button = driver.find_element(By.XPATH, xpath)

        # Click the button
        button.click()
        time.sleep(5)
        print("Button clicked successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

def get_data(driver, xpath):
    '''
    Extracts the text content from an element specified by the XPath on the page.
    '''
    try:
        # Find the element using XPath
        data = driver.find_element(By.XPATH, xpath)
        # Return the text content of the element
        return data.text.strip()
    except Exception as e:
        print(f"An error occurred while extracting the text: {e}")
        return None

def login(driver, email, password, login_page_link):
    '''
    Logs in to the LinkedIn account.
    '''
    open_page(driver, login_page_link)
    time.sleep(5)  # Wait for the page to load

    try:
        # Locate and fill in the username and password fields
        username_field = driver.find_element(By.ID, 'username')
        username_field.send_keys(email)

        password_field = driver.find_element(By.ID, 'password')
        password_field.send_keys(password)

        password_field.send_keys(Keys.RETURN)
        time.sleep(5)  # Wait for login to process

        # Check if login was successful by checking the title of the page
        if "Feed | LinkedIn" in driver.title:
            print("Login successful!")
            return True
        else:
            print("Login failed. Check your credentials or other login issues.")
            return False

    except Exception as e:
        print(f"Exception occurred during login: {e}")
        return False



def get_experience(driver):
    experiences = []
    print("List created")

    try:
        # Identify all experience elements dynamically
        experience_elements = driver.find_elements(By.XPATH, '/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section/div[2]/div/div[1]/ul/li')
        print(f"Found {len(experience_elements)} experience entries")

        # Loop through each element and extract the text
        for element in experience_elements:
            raw_text = element.text.split("\n")  # Split text into lines
            cleaned_text = list(dict.fromkeys(raw_text))  # Remove duplicates while preserving order
            experiences.append(cleaned_text)  # Append cleaned data to the list
    except Exception as e:
        print(f"An error occurred while fetching experiences: {e}")
    
    return experiences


def get_education(driver):
    education = []
    print("List created")

    try:
        # Identify all experience elements dynamically
        education_elements = driver.find_elements(By.XPATH, '/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[5]/div[3]/ul/li')
        print(f"Found {len(education_elements)} experience entries")

        # Loop through each element and extract the text
        for element in education_elements:
            raw_text = element.text.split("\n")  # Split text into lines
            cleaned_text = list(dict.fromkeys(raw_text))  # Remove duplicates while preserving order
            education.append(cleaned_text)  # Append cleaned data to the list
    except Exception as e:
        print(f"An error occurred while fetching experiences: {e}")
    
    return education
  

def save_to_csv(name, bio, location, experience_list, education_list, filename='scraped_data.csv'):
    """
    Saves the scraped data to a CSV file.

    Parameters:
    - name: Name of the person
    - bio: Bio of the person
    - location: Location of the person
    - experience_list: List of experience details (each item in the list is a list of role, company, duration, location)
    - education_list: List of education details (each item in the list is a list of degree, institution, duration)
    - filename: Name of the CSV file to save data to (default is 'scraped_data.csv')

    Returns:
    - None
    """
    try:
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            
            # Write header row
            writer.writerow(['Name', 'Bio', 'Location', 'Experience Role', 'Experience Company', 'Experience Duration', 'Experience Location', 'Education Degree', 'Education Institution', 'Education Duration'])
            
            # Write data
            for exp, edu in zip(experience_list, education_list):
                # Extract experience details
                experience_role = exp[0]
                experience_company = exp[1]
                experience_duration = exp[2]
                experience_location = exp[3]
                
                # Extract education details
                education_degree = edu[0]
                education_institution = edu[1]
                education_duration = edu[2]
                
                # Write all data to the CSV
                writer.writerow([name, bio, location, experience_role, experience_company, experience_duration, experience_location, education_degree, education_institution, education_duration])

        print(f"Data successfully saved to {filename}")
    
    except Exception as e:
        print(f"Error occurred while saving data to CSV: {e}")
